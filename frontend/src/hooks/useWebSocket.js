import { useCallback, useRef } from 'react';
import useGameStore from '../store/gameStore';

const useWebSocket = () => {
  const socketRef = useRef(null);

  const {
    setSocket,
    setConnected,
    setPlayers,
    setGameState,
    setGamePhase,
    setCurrentPlayer,
    setLandlord,
    setHandCards,
    setLastPlay,
    setPassCount,
    incrementRound,
    addChatMessage,
    resetGameState
  } = useGameStore();

  const connect = useCallback((roomId, playerName) => {
    // 如果已经连接，先断开
    if (socketRef.current) {
      socketRef.current.close();
    }

    // 构建WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = process.env.NODE_ENV === 'development' ? '8000' : window.location.port;
    const wsUrl = `${protocol}//${host}:${port}/ws/${roomId}/${encodeURIComponent(playerName)}`;

    console.log('Connecting to:', wsUrl);

    try {
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket连接已建立');
        setSocket(socket);
        setConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('收到消息:', message);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      socket.onclose = (event) => {
        console.log('WebSocket连接已关闭:', event.code, event.reason);
        setConnected(false);
        setSocket(null);
        socketRef.current = null;
      };

      socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
        setConnected(false);
      };

    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
    }
  }, [setSocket, setConnected]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    setConnected(false);
    setSocket(null);
  }, [setConnected, setSocket]);

  const handleWebSocketMessage = useCallback((message) => {
    const { type, ...data } = message;

    switch (type) {
      case 'player_joined':
        console.log('玩家加入:', data);
        setPlayers(data.players || []);
        break;

      case 'player_left':
        console.log('玩家离开:', data);
        setPlayers(data.players || []);
        break;

      case 'game_state':
        console.log('游戏状态更新:', data);
        handleGameStateUpdate(data);
        break;

      case 'game_start':
        console.log('游戏开始');
        setGamePhase('playing');
        break;

      case 'game_end':
        console.log('游戏结束:', data);
        handleGameEnd(data);
        break;

      case 'cards_played':
        console.log('有玩家出牌:', data);
        handleCardsPlayed(data);
        break;

      case 'player_passed':
        console.log('有玩家过牌:', data);
        handlePlayerPassed(data);
        break;

      case 'chat':
        console.log('聊天消息:', data);
        addChatMessage({
          player_name: data.player_name,
          message: data.message,
          timestamp: data.timestamp || Date.now()
        });
        break;

      case 'error':
        console.error('服务器错误:', data.message);
        break;

      case 'game_restart':
        console.log('游戏重新开始:', data.message);
        resetGameState();
        break;

      default:
        console.log('未处理的消息类型:', type, data);
    }
  }, [
    setPlayers,
    setGamePhase,
    addChatMessage,
    resetGameState
  ]);

  const handleGameStateUpdate = useCallback((data) => {
    const { game_info, your_cards, your_index, players } = data;

    if (game_info) {
      setGameState(game_info);
      setGamePhase(game_info.phase);
      setCurrentPlayer(game_info.current_player_idx);

      if (game_info.landlord_idx !== null) {
        setLandlord(game_info.landlord_idx);
      }

      if (game_info.last_play) {
        setLastPlay(game_info.last_play, game_info.last_play.player_idx);
      }

      setPassCount(game_info.pass_count);
    }

    if (your_cards) {
      setHandCards(your_cards);
    }

    if (players) {
      setPlayers(players.map(p => p.name));
    }
  }, [
    setGameState,
    setGamePhase,
    setCurrentPlayer,
    setLandlord,
    setLastPlay,
    setPassCount,
    setHandCards,
    setPlayers
  ]);

  const handleCardsPlayed = useCallback((data) => {
    const { player_name, cards, card_type } = data;
    console.log(`${player_name} 出牌:`, cards, card_type);

    // 更新最后出牌信息
    setLastPlay({
      cards: cards,
      card_type: card_type,
      player_name: player_name
    });

    incrementRound();
  }, [setLastPlay, incrementRound]);

  const handlePlayerPassed = useCallback((data) => {
    const { player_name } = data;
    console.log(`${player_name} 过牌`);

    incrementRound();
  }, [incrementRound]);

  const handleGameEnd = useCallback((data) => {
    const { result } = data;
    console.log('游戏结束:', result);

    // 可以在这里显示游戏结果
    addChatMessage({
      player_name: '系统',
      message: `游戏结束！${result.result}`,
      timestamp: Date.now()
    });

    // 延迟重置游戏状态
    setTimeout(() => {
      resetGameState();
    }, 5000);
  }, [addChatMessage, resetGameState]);

  const sendMessage = useCallback((message) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
      return true;
    }
    console.error('WebSocket未连接，无法发送消息');
    return false;
  }, []);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected: socketRef.current?.readyState === WebSocket.OPEN
  };
};

export default useWebSocket;