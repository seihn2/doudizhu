import { create } from 'zustand';

const useGameStore = create((set, get) => ({
  // 玩家信息
  playerName: '',
  playerId: null,

  // 房间信息
  roomId: '',
  roomName: '',
  players: [],

  // 游戏状态
  gameState: null,
  gamePhase: 'waiting',
  currentPlayerIdx: 0,
  landlordIdx: null,

  // 手牌
  handCards: [],
  selectedCards: [],

  // 游戏历史
  lastPlay: null,
  lastPlayerIdx: null,
  passCount: 0,
  roundCount: 0,

  // WebSocket连接
  socket: null,
  connected: false,

  // 聊天消息
  chatMessages: [],

  // Actions
  setPlayerInfo: (name, id) => set({ playerName: name, playerId: id }),

  setRoomInfo: (roomId, roomName) => set({ roomId, roomName }),

  setPlayers: (players) => set({ players }),

  setGameState: (gameState) => set({ gameState }),

  setGamePhase: (phase) => set({ gamePhase: phase }),

  setCurrentPlayer: (idx) => set({ currentPlayerIdx: idx }),

  setLandlord: (idx) => set({ landlordIdx: idx }),

  setHandCards: (cards) => set({ handCards: cards }),

  setSelectedCards: (cards) => set({ selectedCards: cards }),

  toggleCardSelection: (cardIndex) => set((state) => {
    const newSelected = [...state.selectedCards];
    const index = newSelected.indexOf(cardIndex);

    if (index > -1) {
      newSelected.splice(index, 1);
    } else {
      newSelected.push(cardIndex);
    }

    return { selectedCards: newSelected };
  }),

  clearSelectedCards: () => set({ selectedCards: [] }),

  setLastPlay: (play, playerIdx) => set({ lastPlay: play, lastPlayerIdx: playerIdx }),

  setPassCount: (count) => set({ passCount: count }),

  incrementRound: () => set((state) => ({ roundCount: state.roundCount + 1 })),

  setSocket: (socket) => set({ socket }),

  setConnected: (connected) => set({ connected }),

  addChatMessage: (message) => set((state) => ({
    chatMessages: [...state.chatMessages, {
      id: Date.now(),
      timestamp: new Date(),
      ...message
    }]
  })),

  clearChatMessages: () => set({ chatMessages: [] }),

  // 重置游戏状态
  resetGameState: () => set({
    gameState: null,
    gamePhase: 'waiting',
    currentPlayerIdx: 0,
    landlordIdx: null,
    handCards: [],
    selectedCards: [],
    lastPlay: null,
    lastPlayerIdx: null,
    passCount: 0,
    roundCount: 0
  }),

  // 重置所有状态
  resetAll: () => set({
    playerName: '',
    playerId: null,
    roomId: '',
    roomName: '',
    players: [],
    gameState: null,
    gamePhase: 'waiting',
    currentPlayerIdx: 0,
    landlordIdx: null,
    handCards: [],
    selectedCards: [],
    lastPlay: null,
    lastPlayerIdx: null,
    passCount: 0,
    roundCount: 0,
    socket: null,
    connected: false,
    chatMessages: []
  }),

  // 游戏动作
  playCards: () => {
    const { selectedCards, handCards, socket, roomId, playerName } = get();

    if (selectedCards.length === 0) {
      return false;
    }

    const cardsToPlay = selectedCards.map(index => handCards[index]);

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'play_cards',
        cards: cardsToPlay,
        player_name: playerName
      }));

      set({ selectedCards: [] });
      return true;
    }

    return false;
  },

  pass: () => {
    const { socket, playerName } = get();

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'pass',
        player_name: playerName
      }));
      return true;
    }

    return false;
  },

  sendChatMessage: (message) => {
    const { socket, playerName } = get();

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'chat',
        message,
        player_name: playerName
      }));
      return true;
    }

    return false;
  }
}));

export default useGameStore;