import asyncio
import signal
from typing import Callable, List
from ..hal.base import HardwareRegistry

class ServiceRunner:
    def __init__(self, config=None):
        self.config = config or {}
        self.tasks: List[asyncio.Task] = []
        self.hal: HardwareRegistry = HardwareRegistry()
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._health = {"ready": False, "alive": True}
        self._on_shutdown: List[Callable[[], None]] = []

    async def start(self):
        if self._running:
            return
        # Initialize HAL and mark ready
        await self.hal.initialize_all()
        self._running = True
        self._health["ready"] = True
        # Start background monitor task
        self.tasks.append(asyncio.create_task(self._monitor()))

    async def stop(self):
        if not self._running:
            return
        self._health["ready"] = False
        # Signal tasks to stop
        self._shutdown_event.set()
        # cancel background tasks
        for t in list(self.tasks):
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
        # shutdown HAL
        await self.hal.shutdown_all()
        # run on_shutdown callbacks
        for cb in self._on_shutdown:
            try:
                cb()
            except Exception:
                pass
        self._running = False

    async def _monitor(self):
        # simple periodic health monitor placeholder
        try:
            while not self._shutdown_event.is_set():
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass

    def register_shutdown_callback(self, cb: Callable[[], None]):
        self._on_shutdown.append(cb)

    def is_ready(self) -> bool:
        return bool(self._health.get("ready", False))

    def is_alive(self) -> bool:
        return bool(self._health.get("alive", True))


# Helper to install signal handlers when running as a script
def install_signal_handlers(runner: ServiceRunner):
    loop = asyncio.get_event_loop()

    def _handle_exit(signame):
        async def _shutdown():
            try:
                await runner.stop()
            finally:
                loop.stop()

        asyncio.ensure_future(_shutdown())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: _handle_exit(s.name))
        except NotImplementedError:
            # add_signal_handler may not be available on Windows or some event loops
            pass
