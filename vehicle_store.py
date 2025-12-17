import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

class VehicleStore:
    def __init__(self, hass: HomeAssistant, store: Store):
        self.hass = hass
        self.store = store
        self.vehicles = {}
        self._listeners = []

    def add_listener(self, callback):
        """Registrace callbacku pro aktualizaci senzorů."""
        self._listeners.append(callback)

    def _notify_listeners(self):
        """Upozorní senzory, že se data změnila."""
        for callback in self._listeners:
            callback()

    async def async_load(self):
        data = await self.store.async_load()
        if data:
            self.vehicles = data
        else:
            self.vehicles = {}
        _LOGGER.debug("Loaded vehicles: %s", self.vehicles)

    async def async_save(self):
        await self.store.async_save(self.vehicles)

    async def add_refuel(self, vehicle_id, date, liters, price_per_l, odometer):
        if vehicle_id not in self.vehicles:
            self.vehicles[vehicle_id] = {
                "refuels": [],
                "service": [],
                "insurance": None,
                "tech_check": None,
            }
        
        # Ošetření, aby klíč existoval i u starších záznamů
        if "refuels" not in self.vehicles[vehicle_id]:
             self.vehicles[vehicle_id]["refuels"] = []

        self.vehicles[vehicle_id]["refuels"].append({
            "date": date,
            "liters": liters,
            "price_per_l": price_per_l,
            "odometer": odometer
        })
        
        await self.async_save()
        _LOGGER.info("Added refuel for %s", vehicle_id)
        
        # Upozorníme senzory na změnu
        self._notify_listeners()