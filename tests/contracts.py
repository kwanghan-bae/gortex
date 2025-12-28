import unittest
import time
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStorageContract(ABC):
    """
    Contract test for BaseStorage implementations.
    Any Storage implementation must pass these tests.
    """

    @abstractmethod
    def get_storage(self):
        """Returns the storage instance to test."""
        pass

    def test_basic_crud(self):
        storage = self.get_storage()
        key = "test:key:1"
        value = "hello_world"

        # Create
        storage.set(key, value)

        # Read
        assert storage.get(key) == value

        # Update
        new_value = "updated_world"
        storage.set(key, new_value)
        assert storage.get(key) == new_value

        # Delete
        storage.delete(key)
        assert storage.get(key) is None

    def test_expiration(self):
        storage = self.get_storage()
        key = "test:expire"
        value = "temporary"

        storage.set(key, value, ex=1)
        assert storage.get(key) == value

        # Wait for expiration
        time.sleep(1.2)
        assert storage.get(key) is None

    def test_keys_listing(self):
        storage = self.get_storage()
        # Clean up first
        for k in storage.keys("test:list:*"):
            storage.delete(k)

        storage.set("test:list:1", "v1")
        storage.set("test:list:2", "v2")
        storage.set("test:list:other", "v3")

        keys = storage.keys("test:list:*")
        assert len(keys) == 3
        assert "test:list:1" in keys
        assert "test:list:2" in keys


class BaseMessageBusContract(ABC):
    """
    Contract test for BaseMessageBus implementations.
    """

    @abstractmethod
    def get_bus(self):
        """Returns the bus instance to test."""
        pass

    def test_publish_subscribe(self):
        bus = self.get_bus()
        received = []

        def callback(msg):
            received.append(msg)

        channel = "test:pubsub"
        bus.listen(channel, callback)

        payload = {"foo": "bar"}
        bus.publish_event(channel, "Tester", "test_event", payload)

        # Wait a bit for processing
        time.sleep(0.1)

        assert len(received) == 1
        assert received[0]["type"] == "test_event"
        assert received[0]["payload"] == payload

    def test_queues(self):
        bus = self.get_bus()
        # Queue testing might depend on implementation details (Local uses internal list)
        # Assuming enqueue_task puts it somewhere.
        # Since BaseMessageBus defines enqueue_task, we should test it doesn't crash.
        # But retrieval isn't in BaseMessageBus interface for workers yet (implementation specific).
        # So we just test basic invocation.
        bus.enqueue_task("test:queue", {"task": 1})

    def test_locking(self):
        bus = self.get_bus()
        lock_name = "test:lock"

        # Acquire
        assert bus.acquire_lock(lock_name, timeout=2) is True

        # Re-acquire (should fail)
        assert bus.acquire_lock(lock_name, timeout=2) is False

        # Release
        bus.release_lock(lock_name)

        # Acquire again
        assert bus.acquire_lock(lock_name, timeout=2) is True
