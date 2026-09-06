CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    size INTEGER NOT NULL,
    initial_board TEXT NOT NULL,    -- store board as JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS games (
  id TEXT PRIMARY KEY,
  user_id INTEGER NULL, -- NULL indicates games played by guests
  board_id INTEGER NULL, -- NULL indicates games with randomly generated boards
  
  board_size INTEGER NOT NULL,
  game_mode TEXT NOT NULL DEFAULT 'mixed', -- 'mixed', 'all_on', 'all_off'
  ruleset TEXT NOT NULL DEFAULT 'color_flip', -- 'color_flip', 'lights_out', etc.
  seed INTEGER NULL,
  
  -- Board configurations AS JSON serialized strings
  initial_board TEXT NOT NULL, -- store board as JSON string
  current_board TEXT NOT NULL, -- store board as JSON string

  -- Event history for undo/redo
  moves_history TEXT NOT NULL DEFAULT '[]', -- array of coordinates, e.g. [[0,1],[2,2]]
  moves_count INTEGER NOT NULL DEFAULT 0,
  
  time_elapsed REAL NOT NULL DEFAULT 0.0,
  is_completed BOOLEAN NOT NULL DEFAULT 0,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
  FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE SET NULL
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_games_user_id ON games(user_id);
CREATE INDEX IF NOT EXISTS idx_games_board_id ON games(board_id);
