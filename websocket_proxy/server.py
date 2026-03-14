"""
WebSocket Proxy Server for Best-Option
Handles client connections and routes market data from brokers
"""
import asyncio
import json
import os
from collections import defaultdict

import websockets
import zmq
import zmq.asyncio

from database.auth_db import get_broker_auth
from database.user_db import get_user_by_id
from utils.logging import get_logger

from .mapping import SymbolMapper

logger = get_logger("websocket_proxy")


class WebSocketProxy:
    """
    WebSocket Proxy Server that handles client connections,
    manages subscriptions, and routes market data from broker adapters to clients
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        """
        Initialize the WebSocket Proxy

        Args:
            host: Hostname to bind the WebSocket server to
            port: Port number to bind the WebSocket server to
        """
        self.host = host
        self.port = port
        self.clients = {}  # Maps client_id to websocket connection
        self.subscriptions = {}  # Maps client_id to set of subscriptions
        self.user_mapping = {}  # Maps client_id to user_id
        self.running = False

        # Subscription index for O(1) lookup
        # Maps (symbol, exchange, mode) -> set of client_ids
        self.subscription_index = defaultdict(set)

        # ZeroMQ context for subscribing to broker adapters
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        
        # Connect to ZMQ
        ZMQ_HOST = os.getenv("ZMQ_HOST", "127.0.0.1")
        ZMQ_PORT = os.getenv("ZMQ_PORT", "5555")
        self.socket.connect(f"tcp://{ZMQ_HOST}:{ZMQ_PORT}")
        
        # Subscribe to all messages
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")

    async def start(self):
        """Start the WebSocket server and ZeroMQ listener"""
        self.running = True

        try:
            # Start ZeroMQ listener
            logger.info("Starting ZeroMQ listener task")
            loop = asyncio.get_running_loop()
            zmq_task = loop.create_task(self.zmq_listener())

            # Start WebSocket server
            logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
            
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"WebSocket server started on {self.host}:{self.port}")
                # Keep running until stopped
                while self.running:
                    await asyncio.sleep(1)

        except Exception as e:
            logger.exception(f"Error in start method: {e}")
            raise

    async def stop(self):
        """Stop the WebSocket server and clean up resources"""
        logger.info("Stopping WebSocket server...")
        self.running = False

        try:
            # Close all client connections
            for client_id, websocket in self.clients.items():
                try:
                    await websocket.close()
                except Exception as e:
                    logger.exception(f"Error closing client {client_id}: {e}")

            # Close ZeroMQ socket
            if hasattr(self, "socket") and self.socket:
                self.socket.close()

            # Close ZeroMQ context
            if hasattr(self, "context") and self.context:
                self.context.term()

            logger.info("WebSocket server stopped")

        except Exception as e:
            logger.exception(f"Error during stop: {e}")

    async def zmq_listener(self):
        """Listen for market data from broker adapters via ZeroMQ"""
        logger.info("ZeroMQ listener started")
        
        try:
            while self.running:
                try:
                    # Receive message from broker adapter
                    [topic, data] = await self.socket.recv_multipart()
                    topic_str = topic.decode("utf-8")
                    data_dict = json.loads(data.decode("utf-8"))

                    # Extract symbol, exchange, mode from topic
                    # Topic format: "SYMBOL_EXCHANGE_MODE"
                    parts = topic_str.split("_")
                    if len(parts) >= 3:
                        symbol = "_".join(parts[:-2])
                        exchange = parts[-2]
                        mode = parts[-1]

                        # Find clients subscribed to this data
                        sub_key = (symbol, exchange, mode)
                        if sub_key in self.subscription_index:
                            clients = self.subscription_index[sub_key]
                            
                            # Send to all subscribed clients
                            for client_id in clients:
                                if client_id in self.clients:
                                    try:
                                        await self.clients[client_id].send(json.dumps(data_dict))
                                    except Exception as e:
                                        logger.exception(f"Error sending to client {client_id}: {e}")

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.exception(f"Error in ZMQ listener: {e}")
                    await asyncio.sleep(0.1)

        except Exception as e:
            logger.exception(f"Fatal error in ZMQ listener: {e}")

    async def handle_client(self, websocket):
        """Handle a client connection"""
        client_id = id(websocket)
        self.clients[client_id] = websocket
        self.subscriptions[client_id] = set()

        logger.info(f"Client connected: {client_id}")

        try:
            async for message in websocket:
                try:
                    await self.process_client_message(client_id, message)
                except Exception as e:
                    logger.exception(f"Error processing message from client {client_id}: {e}")
                    await self.send_error(client_id, "PROCESSING_ERROR", str(e))
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.exception(f"Error handling client {client_id}: {e}")
        finally:
            await self.cleanup_client(client_id)

    async def cleanup_client(self, client_id):
        """Clean up client resources when they disconnect"""
        # Remove from subscription index
        if client_id in self.subscriptions:
            for sub_json in self.subscriptions[client_id]:
                try:
                    sub_info = json.loads(sub_json)
                    symbol = sub_info.get("symbol")
                    exchange = sub_info.get("exchange")
                    mode = sub_info.get("mode", "LTP")

                    sub_key = (symbol, exchange, mode)
                    if sub_key in self.subscription_index:
                        self.subscription_index[sub_key].discard(client_id)
                        if not self.subscription_index[sub_key]:
                            del self.subscription_index[sub_key]
                except Exception as e:
                    logger.exception(f"Error cleaning up subscription: {e}")

            del self.subscriptions[client_id]

        # Remove from clients and user mapping
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.user_mapping:
            del self.user_mapping[client_id]

    async def process_client_message(self, client_id, message):
        """Process messages from a client"""
        try:
            data = json.loads(message)
            action = data.get("action") or data.get("type")

            if action in ["authenticate", "auth"]:
                await self.authenticate_client(client_id, data)
            elif action == "subscribe":
                await self.subscribe_client(client_id, data)
            elif action == "unsubscribe":
                await self.unsubscribe_client(client_id, data)
            elif action == "ping":
                await self.handle_ping(client_id, data)
            else:
                await self.send_error(client_id, "INVALID_ACTION", f"Invalid action: {action}")

        except json.JSONDecodeError:
            await self.send_error(client_id, "INVALID_JSON", "Invalid JSON message")
        except Exception as e:
            logger.exception(f"Error processing client message: {e}")
            await self.send_error(client_id, "SERVER_ERROR", str(e))

    async def authenticate_client(self, client_id, data):
        """Authenticate a client using their user_id"""
        user_id = data.get("user_id")

        if not user_id:
            await self.send_error(client_id, "AUTHENTICATION_ERROR", "user_id is required")
            return

        # Verify user exists
        user = get_user_by_id(user_id)
        if not user:
            await self.send_error(client_id, "AUTHENTICATION_ERROR", "Invalid user_id")
            return

        # Store user mapping
        self.user_mapping[client_id] = user_id

        # Send success response
        await self.send_message(client_id, {
            "type": "authenticated",
            "status": "success",
            "user_id": user_id,
            "broker": user.broker
        })

    async def subscribe_client(self, client_id, data):
        """Subscribe client to market data"""
        # Verify client is authenticated
        if client_id not in self.user_mapping:
            await self.send_error(client_id, "NOT_AUTHENTICATED", "Please authenticate first")
            return

        symbol = data.get("symbol")
        exchange = data.get("exchange")
        mode = data.get("mode", "LTP")

        if not symbol or not exchange:
            await self.send_error(client_id, "INVALID_REQUEST", "symbol and exchange are required")
            return

        # Add to subscriptions
        sub_json = json.dumps({"symbol": symbol, "exchange": exchange, "mode": mode})
        self.subscriptions[client_id].add(sub_json)

        # Add to subscription index
        sub_key = (symbol, exchange, mode)
        self.subscription_index[sub_key].add(client_id)

        # Send success response
        await self.send_message(client_id, {
            "type": "subscribed",
            "status": "success",
            "symbol": symbol,
            "exchange": exchange,
            "mode": mode
        })

    async def unsubscribe_client(self, client_id, data):
        """Unsubscribe client from market data"""
        symbol = data.get("symbol")
        exchange = data.get("exchange")
        mode = data.get("mode", "LTP")

        if not symbol or not exchange:
            await self.send_error(client_id, "INVALID_REQUEST", "symbol and exchange are required")
            return

        # Remove from subscriptions
        sub_json = json.dumps({"symbol": symbol, "exchange": exchange, "mode": mode})
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(sub_json)

        # Remove from subscription index
        sub_key = (symbol, exchange, mode)
        if sub_key in self.subscription_index:
            self.subscription_index[sub_key].discard(client_id)
            if not self.subscription_index[sub_key]:
                del self.subscription_index[sub_key]

        # Send success response
        await self.send_message(client_id, {
            "type": "unsubscribed",
            "status": "success",
            "symbol": symbol,
            "exchange": exchange,
            "mode": mode
        })

    async def handle_ping(self, client_id, data):
        """Handle ping request"""
        await self.send_message(client_id, {
            "type": "pong",
            "timestamp": data.get("timestamp")
        })

    async def send_message(self, client_id, message):
        """Send message to a client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except Exception as e:
                logger.exception(f"Error sending message to client {client_id}: {e}")

    async def send_error(self, client_id, code, message):
        """Send error message to a client"""
        await self.send_message(client_id, {
            "type": "error",
            "code": code,
            "message": message
        })
