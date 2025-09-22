import { useState, useCallback, useRef } from 'react';
import axios from 'axios';

const useSingleGameLogic = () => {
  const [gameId, setGameId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [currentPlayer, setCurrentPlayer] = useState(0);
  const [myCards, setMyCards] = useState([]);
  const [lastPlay, setLastPlay] = useState(null);
  const [playHistory, setPlayHistory] = useState([]);
  const [isGameOver, setIsGameOver] = useState(false);
  const [winner, setWinner] = useState(null);
  const [loading, setLoading] = useState(false);
  const pollRef = useRef(null);

  // API基础URL
  const API_BASE = process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'
    : window.location.origin;

  // 更新游戏状态
  const updateGameState = useCallback((gameStateData) => {
    if (!gameStateData) return;

    const { game_info, player_cards, last_play, play_history, players, is_game_over, winner } = gameStateData;

    if (game_info) {
      setGameState(game_info);
      setCurrentPlayer(game_info.current_player_idx);
    }

    if (player_cards) {
      setMyCards(player_cards);
    }

    if (last_play) {
      setLastPlay(last_play);
    }

    if (play_history) {
      setPlayHistory(play_history);
    }

    setIsGameOver(is_game_over || false);
    if (winner) {
      setWinner({ name: winner });
    }
  }, []);

  // 轮询游戏状态
  const pollGameState = useCallback(async (gameId) => {
    if (!gameId) return;

    try {
      const response = await axios.get(`${API_BASE}/api/single-game/${gameId}`);
      if (response.data.success) {
        updateGameState(response.data.game_state);
      }
    } catch (error) {
      console.error('轮询游戏状态失败:', error);
    }
  }, [API_BASE, updateGameState]);

  // 开始轮询
  const startPolling = useCallback((gameId) => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
    }

    pollRef.current = setInterval(() => {
      pollGameState(gameId);
    }, 1000); // 每秒轮询一次
  }, [pollGameState]);

  const startGame = useCallback(async (playerName) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/single-game/create`, null, {
        params: { player_name: playerName }
      });

      if (response.data.success) {
        const newGameId = response.data.game_id;
        setGameId(newGameId);
        updateGameState(response.data.game_state);

        // 开始轮询游戏状态
        startPolling(newGameId);
      } else {
        console.error('创建游戏失败:', response.data.error);
      }
    } catch (error) {
      console.error('创建游戏请求失败:', error);
    } finally {
      setLoading(false);
    }
  }, [API_BASE, updateGameState, startPolling]);


  const playCards = useCallback(async (cards) => {
    if (!gameId || currentPlayer !== 0 || loading) return false;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/single-game/${gameId}/play`, cards);

      if (response.data.success) {
        updateGameState(response.data.game_state);
        return true;
      } else {
        console.error('出牌失败:', response.data.error);
        return false;
      }
    } catch (error) {
      console.error('出牌请求失败:', error);
      return false;
    } finally {
      setLoading(false);
    }
  }, [gameId, currentPlayer, loading, API_BASE, updateGameState]);

  const pass = useCallback(async () => {
    if (!gameId || currentPlayer !== 0 || loading) return false;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/single-game/${gameId}/pass`);

      if (response.data.success) {
        updateGameState(response.data.game_state);
        return true;
      } else {
        console.error('过牌失败:', response.data.error);
        return false;
      }
    } catch (error) {
      console.error('过牌请求失败:', error);
      return false;
    } finally {
      setLoading(false);
    }
  }, [gameId, currentPlayer, loading, API_BASE, updateGameState]);

  const getAIPlayerCards = useCallback((playerIdx) => {
    if (!gameState || !gameState.players_card_count) return 0;
    return gameState.players_card_count[playerIdx] || 0;
  }, [gameState]);

  const isMyTurn = currentPlayer === 0;

  // 清理函数
  const cleanup = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  return {
    gameId,
    gameState,
    currentPlayer,
    myCards,
    lastPlay,
    playHistory,
    isMyTurn,
    isGameOver,
    winner,
    loading,
    startGame,
    playCards,
    pass,
    getAIPlayerCards,
    cleanup
  };
};

export default useSingleGameLogic;