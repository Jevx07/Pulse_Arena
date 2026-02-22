# Pulse Arena — Product Requirements Document

---

## Current State: Phase 1 ✅ Complete

Pulse Arena has a strong, production-ready core. The engine is modular, the combat is responsive, and the feedback loops are polished.

### Architecture

| Module                        | Status | Notes                                                  |
| ----------------------------- | ------ | ------------------------------------------------------ |
| `GameManager`                 | ✅     | Central orchestrator for all entity state              |
| `CombatSystem`                | ✅     | Stateless hitscan pipeline (raycasting, crits, damage) |
| `systems/collision.py`        | ✅     | Collision resolution extracted to its own system       |
| `systems/wave_manager.py`     | ✅     | Enemy spawning and wave progression                    |
| `ui/` (hud, crosshair, menus) | ✅     | Fully decoupled, screen-aware drawing functions        |
| `config/settings.py`          | ✅     | Centralized color palette and game constants           |

### Gameplay

| Feature            | Detail                                                       |
| ------------------ | ------------------------------------------------------------ |
| **Hitscan Combat** | Raycasting with 0.1 radian aim-cone tolerance                |
| **Damage Model**   | 25 base HP, 15% crit chance at 2.0x multiplier               |
| **Weapon State**   | 30-round mag, 2s reload, 10-frame fire rate lock             |
| **Combo Engine**   | 180-frame (3s) kill window, +10% score per combo level       |
| **Feedback Loops** | Hitmarker (10f), screen flash (5f), screen shake (2–6)       |
| **Particle FX**    | Muzzle flash (8 particles), death burst (25), hit sparks (5) |
| **Powerups**       | 30% drop chance on kill, random type (damage/speed/shield)   |
| **HUD**            | Adaptive health bar, combo animator, reload progress bar     |

---

## Phase 2: Decision Engineering 🚨

> The goal of Phase 2 is **not** visual complexity. It is **decision density** — giving players meaningful choices every few seconds.

---

### Priority 1 — Enemy Behavioral Archetypes

**Impact: ⭐⭐⭐⭐⭐ | Difficulty: Medium**

Currently enemies are stat variations. Phase 2 requires **behavioral archetypes** that force the player to make kill-priority decisions.

| Archetype   | Color     | Behavior                                                            | Tactical Role                |
| ----------- | --------- | ------------------------------------------------------------------- | ---------------------------- |
| **Hunter**  | 🟥 Red    | Actively flanks, avoids direct approach, slightly predicts movement | Pressure / aggression        |
| **Sniper**  | 🟨 Yellow | Stops, shows 1s laser indicator, fires hitscan shot                 | Zone control / repositioning |
| **Support** | 🟦 Blue   | Heals/buffs nearby enemies slowly, low mobility                     | Tactical priority target     |

**Files to create/modify:**

- `entities/enemy_hunter.py`, `entities/enemy_sniper.py`, `entities/enemy_support.py`
- `systems/wave_manager.py` — spawn archetype mixes per wave

---

### Priority 2 — Weapon Identity System

**Impact: ⭐⭐⭐⭐ | Difficulty: Medium**

One weapon = one playstyle is a depth limiter.

| Weapon      | Fire Rate       | Damage       | Special                  |
| ----------- | --------------- | ------------ | ------------------------ |
| Rifle       | Medium (10f)    | 25           | Balanced default         |
| SMG         | Fast (4f)       | 10           | High ammo (60 rounds)    |
| Shotgun     | Slow (30f)      | 15×5 pellets | Spread cone              |
| Railgun     | Very slow (60f) | 120          | Charge shot, wall-pierce |
| Burst Rifle | Burst (3×5f)    | 20           | 3-round burst group      |

**Files to create:**

- `systems/weapon_system.py` — `Weapon` dataclass + `WeaponSystem` handler
- `data/weapons.json` — weapon stat definitions (see Priority 6)

---

### Priority 3 — Mid-Match Upgrade Choices

**Impact: ⭐⭐⭐⭐ | Difficulty: Medium**

After each wave clear, present the player with **1-of-3 random upgrade choices**. This makes every run feel distinct.

| Upgrade      | Effect                          |
| ------------ | ------------------------------- |
| Damage Surge | +15% damage (permanent, stacks) |
| Speed Loader | Reload time −25%                |
| Lifesteal    | +5 HP on kill                   |
| Dash         | Adds dash ability (cooldown 2s) |
| Crit Focus   | +10% crit chance                |

**Files to create/modify:**

- `systems/upgrade_system.py` — upgrade pool, roll logic
- `ui/upgrade_menu.py` — 3-card selection screen
- `core/game_manager.py` — hook into wave completion event

---

### Priority 4 — Advanced Feedback Layer (Game Feel)

**Impact: ⭐⭐⭐ | Difficulty: Easy**

The game already has feedback. These additions greatly increase **perceived polish**:

- Hit sound pitch scales proportionally with damage dealt
- Enemies briefly flash white and slow by 30% for 5 frames on impact
- Camera applies a directional recoil impulse (not random shake) on firing
- Crosshair gap expands by 8px when firing, decays over 10 frames
- Directional hit indicator (arrow on screen edge facing damage source)

---

### Priority 5 — Mode Architecture

**Impact: ⭐⭐⭐⭐⭐ | Difficulty: Medium**

Restructure for extensibility. `GameManager` should delegate to an active **Mode** object.

```
core/
    modes/
        survival_mode.py   ← current wave logic moved here
        (pvp_mode.py)      ← future
        (challenge_mode.py) ← future
```

`GameManager.update()` becomes:

```python
self.active_mode.update(self)
```

---

### Priority 6 — Data-Driven Configuration

**Impact: ⭐⭐⭐⭐ | Difficulty: Easy**

All numerical constants should live in JSON, not Python source. This allows balancing without code changes.

```
data/
    enemies.json
    weapons.json
    powerups.json
```

**Example `enemies.json`:**

```json
{
  "rusher": { "speed": 2.2, "health": 60, "damage": 10, "score": 100 },
  "sniper": { "speed": 0.5, "health": 40, "damage": 35, "score": 150 }
}
```

---

### Priority 7 — Retention System

**Impact: ⭐⭐⭐⭐ | Difficulty: Easy**

Persistent session statistics create long-term engagement and are a prerequisite for future leaderboards/matchmaking.

**File:** `data/profile.json`

```json
{
  "highest_wave": 12,
  "total_kills": 847,
  "accuracy_pct": 63.4,
  "longest_combo": 11
}
```

---

## Impact vs. Effort Summary

| Feature          | Impact     | Difficulty | Priority |
| ---------------- | ---------- | ---------- | -------- |
| Enemy Archetypes | ⭐⭐⭐⭐⭐ | Medium     | 1st      |
| Weapon System    | ⭐⭐⭐⭐   | Medium     | 2nd      |
| Upgrade Choices  | ⭐⭐⭐⭐   | Medium     | 3rd      |
| Feedback Polish  | ⭐⭐⭐     | Easy       | 4th      |
| Mode Abstraction | ⭐⭐⭐⭐⭐ | Medium     | 5th      |
| Data Configs     | ⭐⭐⭐⭐   | Easy       | 6th      |
| Retention System | ⭐⭐⭐⭐   | Easy       | 7th      |
