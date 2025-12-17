from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    store = hass.data[DOMAIN]
    sensors = []

    # Vytvoříme senzory pro existující auta
    for vehicle_id in store.vehicles.keys():
        sensors.append(LastRefuelSensor(vehicle_id, store))

    async_add_entities(sensors, True)

class LastRefuelSensor(Entity):
    def __init__(self, vehicle_id, store):
        self._vehicle_id = vehicle_id
        self._store = store
        self._attr_name = f"{vehicle_id} Last Refuel"
        self._attr_unique_id = f"{vehicle_id}_last_refuel"
        self._attr_icon = "mdi:gas-station"
        self._state = None

    async def async_added_to_hass(self):
        """Když je senzor přidán do HA, začne poslouchat změny ve store."""
        self._store.add_listener(self.async_write_ha_state)
        # Prvotní načtení
        self.update_state()

    @callback
    def update_state(self):
        """Vypočítá stav z dat ve store."""
        vehicle_data = self._store.vehicles.get(self._vehicle_id, {})
        refuels = vehicle_data.get("refuels", [])
        if refuels:
            # Vezmeme poslední záznam
            self._state = refuels[-1]["date"]
        else:
            self._state = None

    @property
    def state(self):
        # Aktualizujeme data před vrácením (pro jistotu, nebo spoléháme na listener)
        self.update_state() 
        return self._state