#!/usr/bin/python
import nbt
from data_types import *

NODE_SERVER = 0x01
SERVER_TO_CLIENT = 0x01
FROM_SERVER = 0x01
TO_CLIENT = 0x01

NODE_CLIENT = 0x02
CLIENT_TO_SERVER = 0x02
FROM_CLIENT = 0x02
TO_SERVER = 0x02

other_node = {NODE_CLIENT:NODE_SERVER, NODE_SERVER:NODE_CLIENT}

names = {
    0x00:    "Keep-alive",
    0x01:    "Login request",
    0x02:    "Handshake",
    0x03:    "Chat message",
    0x04:    "Time update",
    0x05:    "Entity Equipment",
    0x06:    "Spawn position",
    0x07:    "Use entity",
    0x08:    "Update health",
    0x09:    "Respawn",
    0x0A:    "Player",
    0x0B:    "Player position",
    0x0C:    "Player look",
    0x0D:    "Player position & look",
    0x0E:    "Player digging",
    0x0F:    "Player block placement",
    0x10:    "Holding change",
    0x11:    "Use bed",
    0x12:    "Animation",
    0x13:    "Entity action",
    0x14:    "Named entity spawn",
    0x15:    "Pickup spawn",
    0x16:    "Collect item",
    0x17:    "Add object/vehicle",
    0x18:    "Mob spawn",
    0x19:    "Entity: painting",
    0x1A:    "Experience orb",
    0x1C:    "Entity velocity",
    0x1D:    "Destroy entity",
    0x1E:    "Entity",
    0x1F:    "Entity relative move",
    0x20:    "Entity look",
    0x21:    "Entity look and relative move",
    0x22:    "Entity teleport",
    0x23:    "Entity head look",
    0x26:    "Entity status",
    0x27:    "Attach entity",
    0x28:    "Entity metadata",
    0x29:    "Entity effect",
    0x2a:    "Remove entity effect",
    0x2b:    "Experience update",
    0x32:    "Pre-chunk",
    0x33:    "Map chunks",
    0x34:    "Multi-block change",
    0x35:    "Block change",
    0x36:    "Block action",
    0x3C:    "Explosion",
    0x3D:    "Sound effect",
    0x46:    "New/invalid state",
    0x47:    "Thunderbolt",
    0x64:    "Open window",
    0x65:    "Close window",
    0x66:    "Window click",
    0x67:    "Set slot",
    0x68:    "Window items",
    0x69:    "Update progress bar",
    0x6A:    "Transaction",
    0x6B:    "Creative inventory action",
    0x6C:    "Enchant Item",
    0x82:    "Update sign",
    0x83:    "Map data",
    0x84:    "Update tile entity",
    0xC8:    "Increment statistic",
    0xC9:    "User list item",
    0xCA:    "Player abilities",
    0xCB:    "Tab-complete",
    0xCC:    "Locale and view distance",
    0xFA:    "Plugin Message",
    0xFE:    "Server list ping",
    0xFF:    "Disconnect"
}
structs = {
    #Keep-alive
    0x00: ("int", "value"),
    #Login request
    0x01:    { 
        CLIENT_TO_SERVER: (
            ("int", "protocol_version"),
            ("string16", "username"),
            ("string16", "not_used_1"),
            ("int", "not_used_2"),
            ("int", "not_used_3"),
            ("byte", "not_used_4"),
            ("byte", "not_used_5"),
            ("ubyte", "not_used_6")),
        SERVER_TO_CLIENT: (
            ("int", "entity_id"),
            ("string16", "not_used_1"),
            ("string16", "level_type"),
            ("int", "game_mode"),
            ("int", "dimension"),
            ("byte", "not_used_2"),
            ("byte", "world_height"),
            ("ubyte", "max_players"))},
    #Handshake
    0x02:    {
        CLIENT_TO_SERVER: ("string16", "username_host"),
        SERVER_TO_CLIENT: ("string16", "connection_hash")},
    #Chat message
    0x03: ("string16", "text"),
    #Time update
    0x04: ("long", "time"),
    #Entity Equipment
    0x05: (
        ("int", "entity_id"),
        ("short", "slot"),
        ("short", "item_id"),
        ("short", "damage")),
    #Spawn position
    0x06: (
        ("int", "x"),
        ("int", "y"),
        ("int", "z")),
    #Use entity
    0x07: (
        ("int", "subject_entity_id"),
        ("int", "object_entity_id"),
        ("bool", "left_click")),
    #Update health
    0x08: (
        ("short", "health"),
        ("short", "food"),
        ("float", "food_saturation")),
    #Respawn
    0x09: (
        ("int", "dimension"),
        ("byte", "difficulty"),
        ("byte", "game_mode"),
        ("short", "world_height"),
        ("string16", "level_type")),
    #Player
    0x0A: ("bool", "on_ground"),
    #Player position
    0x0B: (
        ("double", "x"),
        ("double", "y"),
        ("double", "stance"),
        ("double", "z"),
        ("bool", "on_ground")),
    #Player look
    0x0C: (
        ("float", "yaw"),
        ("float", "pitch"),
        ("bool", "on_ground")),
    #Player position & look
    0x0D:    {
        CLIENT_TO_SERVER: (
            ("double", "x"),
            ("double", "y"),
            ("double", "stance"),
            ("double", "z"),
            ("float", "yaw"),
            ("float", "pitch"),
            ("bool", "on_ground")),
        SERVER_TO_CLIENT: (
            ("double", "x"),
            ("double", "stance"),
            ("double", "y"),
            ("double", "z"),
            ("float", "yaw"),
            ("float", "pitch"),
            ("bool", "on_ground"))},
    #Player digging
    0x0E: (
        ("byte", "status"),
        ("int", "x"),
        ("ubyte", "y"),
        ("int", "z"),
        ("byte", "face")),
    #Player block placement
    0x0F: (
        ("int", "x"),
        ("ubyte", "y"),
        ("int", "z"),
        ("byte", "direction"),
        ("slot", "slot")),
    #Holding change
    0x10: ("short", "slot"),
    #Use bed
    0x11: (
        ("int", "entity_id"),
        ("byte", "in_bed"),
        ("int", "x"),
        ("ubyte", "y"),
        ("int", "z")),
    #Animation
    0x12: (
        ("int", "entity_id"),
        ("byte", "animation")),
    #Entity action
    0x13: (
        ("int", "entity_id"),
        ("byte", "action")),
    #Named entity spawn
    0x14: (
        ("int", "entity_id"),
        ("string16", "player_name"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("byte", "rotation"),
        ("byte", "pitch"),
        ("short", "current_item")),
    #Pickup spawn
    0x15: (
        ("int", "entity_id"),
        ("short", "item"),
        ("byte", "count"),
        ("short", "metadata"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("byte", "rotation"),
        ("byte", "pitch"),
        ("byte", "roll")),
    #Collect item
    0x16: (
        ("int", "subject_entity_id"),
        ("int", "object_entity_id")),
    #Add object/vehicle
    0x17: (
        ("int", "entity_id"),
        ("byte", "type"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("int", "thrower_entity_id")),
    #Mob spawn
    0x18: (
        ("int", "entity_id"),
        ("byte", "type"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("byte", "yaw"),
        ("byte", "pitch"),
        ("byte", "head_yaw"),
        ("metadata", "metadata")),
    #Entity: painting
    0x19: (
        ("int", "entity_id"),
        ("string16", "title"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"), 
        ("int", "direction")),
    #Experience orb
    0x1A: (
        ("int", "entity_id"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("short", "count")),
    #Entity velocity
    0x1C: (
        ("int", "entity_id"),
        ("short", "x_velocity"),
        ("short", "y_velocity"),
        ("short", "z_velocity")),
    #Destroy entity
    0x1D: ("int", "entity_id"),
    #Entity
    0x1E: ("int", "entity_id"),
    #Entity relative move
    0x1F: (
        ("int", "entity_id"),
        ("byte", "x_change"),
        ("byte", "y_change"),
        ("byte", "z_change")),
    #Entity look
    0x20: (
        ("int", "entity_id"),
        ("byte", "yaw"),
        ("byte", "pitch")),
    #Entity look and relative move
    0x21: (
        ("int", "entity_id"),
        ("byte", "x_change"),
        ("byte", "y_change"),
        ("byte", "z_change"),
        ("byte", "yaw"),
        ("byte", "pitch")),
    #Entity teleport
    0x22: (
        ("int", "entity_id"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("byte", "yaw"),
        ("byte", "pitch")),
    #Entity head look
    0x23: (
        ("int", "entity_id"),
        ("byte", "head_yaw")),
    #Entity status
    0x26: (
        ("int", "entity_id"),
        ("byte", "status")),
    #Attach entity
    0x27: (
        ("int", "subject_entity_id"),
        ("int", "object_entity_id")),
    #Entity metadata
    0x28: (
        ("int", "entity_id"),
        ("metadata", "metadata")),
    #Entity effect
    0x29: (
        ("int", "entity_id"),
        ("byte", "effect_id"),
        ("byte", "amplifier"),
        ("short", "duration")),
    #Remove entity effect
    0x2a: (
        ("int", "entity_id"),
        ("byte", "effect_id")),
    #Experience
    0x2b: (
        ("float", "experience_bar_maybe"),
        ("short", "level_maybe"),
        ("short", "total_experience_maybe")),
    #Pre-chunk
    0x32: (
        ("int", "x"),
        ("int", "z"),
        ("bool", "load")),
    #Map chunks
    0x33: (
        ("int", "x_chunk"),
        ("int", "z_chunk"),
        ("bool", "ground_up_contiguous"),
        ("short", "primary_bitmap"),
        ("short", "secondary_bitmap"),
        ("int", "data_size"),
        ("int", "not_used_1")),
    #Multi-block change
    0x34: (
        ("int", "x_chunk"),
        ("int", "z_chunk"),
        ("short", "record_count"),
        ("int", "data_size")),
    #Block change
    0x35: (
        ("int", "x"),
        ("ubyte", "y"),
        ("int", "z"),
        ("byte", "id"),
        ("byte", "metadata")),
    #Block action
    0x36: (
        ("int", "x"),
        ("short", "y"),
        ("int", "z"),
        ("byte", "type_state"),
        ("byte", "pitch_direction")),
    #Explosion
    0x3C: (
        ("double", "x"),
        ("double", "y"),
        ("double", "z"),
        ("float", "radius"),
        ("int", "data_size")),
    #Sound effect
    0x3D: (
        ("int", "effect_id"),
        ("int", "x"),
        ("ubyte", "y"),
        ("int", "z"),
        ("int", "extra")),
    #New/invalid state
    0x46: (
        ("byte", "reason"),
        ("byte", "game_mode")),
    #Thunderbolt
    0x47: (
        ("int", "entity_id"),
        ("bool", "not_used"),
        ("int", "x"),
        ("int", "y"),
        ("int", "z")),
    #Open window
    0x64: (
        ("byte", "window_id"),
        ("byte", "inventory_type"),
        ("string16", "window_title"),
        ("byte", "slots_count")),
    #Close window
    0x65: ("byte", "window_id"),
    #Window click
    0x66: (
        ("byte", "window_id"),
        ("short", "slot"),
        ("byte", "right_click"),
        ("short", "transaction_id"),
        ("bool", "shift"),
        ("slot", "slot_data")),
    #Set slot
    0x67: (
        ("byte", "window_id"),
        ("short", "slot"),
        ("slot", "slot_data")),
    #Window items
    0x68: (
        ("byte", "window_id"),
        ("short", "data_size")),
    #Update progress bar
    0x69: (
        ("byte", "window_id"),
        ("short", "progress_bar_type"),
        ("short", "progress")),
    #Transaction
    0x6A: (
        ("byte", "window_id"),
        ("short", "transaction_id"),
        ("bool", "accepted")),
    
    #Creative inventory action
    0x6B: (
        ("short", "slot"),
        ("slot", "slot_data")),
    #Enchant item
    0x6C: (
        ("byte", "window_id"),
        ("byte", "enchantment")),
    #Update sign
    0x82: (
        ("int", "x"),
        ("short", "y"),
        ("int", "z"),
        ("string16", "line_1"),
        ("string16", "line_2"),
        ("string16", "line_3"),
        ("string16", "line_4")),
    #Map data
    0x83: (
        ("short", "item_id"),
        ("short", "map_id"),
        ("ubyte", "data_size")),
    #Update tile entity
    0x84: (
        ("int", "x"),
        ("short", "y"),
        ("int", "z"),
        ("byte", "action"),
        ("int", "custom_1"),
        ("int", "custom_2"),
        ("int", "custom_3")),
    #Increment statistic
    0xC8: (
        ("int", "statistic_id"),
        ("byte", "amount")),
    #User list
    0xC9: (
        ("string16", "player_name"),
        ("bool", "online"),
        ("short", "ping")),
    #Player abilities
    0xCA: (
        ("bool", "invulnerable"),
        ("bool", "is_flying"),
        ("bool", "can_fly"),
        ("bool", "instabreak")),
    #Tab-complete
    0xCB: ("string16", "text"),
    #Locale and view distance
    0xCC: (
        ("string16", "locale"),
        ("int", "view_distance")),
    #Plugin message
    0xFA: (
        ("string16", "channel"),
        ("short", "data_size")),
    #Server ping
    0xFE: (),
    #Disconnect
    0xFF: ("string16", "reason")}

#Normalise the structs

for key, val in structs.iteritems():
    if isinstance(val, dict):
        for k in (TO_CLIENT, TO_SERVER):
            if len(val[k]) and not isinstance(val[k][0], tuple):
                structs[key][k] = (val[k],)
        continue
    elif len(val) and not isinstance(val[0], tuple):
        val = (val,)
    val = {
        CLIENT_TO_SERVER: val,
        SERVER_TO_CLIENT: val}
    structs[key] = val
