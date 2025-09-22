import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Button, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import useGameStore from '../store/gameStore';
import useWebSocket from '../hooks/useWebSocket';
import GameBoard from './GameBoard';
import PlayerArea from './PlayerArea';
import ChatPanel from './ChatPanel';

const { Title } = Typography;

const GameRoom = () => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const {
    playerName,
    players,
    gamePhase,
    connected,
    setRoomInfo
  } = useGameStore();

  const { connect, disconnect } = useWebSocket();

  useEffect(() => {
    if (!playerName) {
      message.error('请先设置玩家名称');
      navigate('/');
      return;
    }

    // 设置房间信息
    setRoomInfo(roomId, `房间 ${roomId}`);

    // 连接WebSocket
    connect(roomId, playerName);

    return () => {
      disconnect();
    };
  }, [roomId, playerName, navigate, setRoomInfo, connect, disconnect]);

  const handleBack = () => {
    disconnect();
    navigate('/');
  };

  if (!connected) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Card style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          textAlign: 'center',
          padding: 40
        }}>
          <Title level={3}>正在连接游戏服务器...</Title>
          <p>房间ID: {roomId}</p>
          <Button onClick={handleBack}>返回首页</Button>
        </Card>
      </div>
    );
  }

  if (gamePhase === 'waiting') {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}>
        <Card style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          textAlign: 'center',
          padding: 40,
          maxWidth: 500
        }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
            style={{ position: 'absolute', top: 20, left: 20 }}
          >
            返回
          </Button>

          <Title level={2} style={{ color: '#667eea', marginBottom: 30 }}>
            🎮 等待其他玩家加入
          </Title>

          <div style={{ marginBottom: 30 }}>
            <p style={{ fontSize: 16, marginBottom: 10 }}>
              房间ID: <strong>{roomId}</strong>
            </p>
            <p style={{ color: '#666' }}>
              当前玩家: {players.length}/3
            </p>
          </div>

          <div style={{
            background: 'rgba(102, 126, 234, 0.1)',
            borderRadius: '15px',
            padding: 20,
            marginBottom: 20
          }}>
            <Title level={4} style={{ margin: 0, marginBottom: 10 }}>
              已加入玩家:
            </Title>
            {players.map((player, index) => (
              <div key={index} style={{
                background: 'white',
                borderRadius: '10px',
                padding: '10px 15px',
                margin: '5px 0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <span>{player}</span>
                {player === playerName && (
                  <span style={{ color: '#667eea', fontSize: 12 }}>（你）</span>
                )}
              </div>
            ))}
          </div>

          {players.length < 3 && (
            <p style={{ color: '#999' }}>
              等待 {3 - players.length} 名玩家加入...
            </p>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      position: 'relative'
    }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={handleBack}
        style={{
          position: 'absolute',
          top: 20,
          left: 20,
          zIndex: 1000,
          background: 'rgba(255, 255, 255, 0.9)',
          border: 'none'
        }}
      >
        返回
      </Button>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 300px',
        height: '100vh',
        gap: 20,
        padding: 20
      }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {/* 其他玩家区域 */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 20,
            marginBottom: 20,
            height: '200px'
          }}>
            {players.slice(0, 2).map((player, index) => (
              <PlayerArea
                key={index}
                player={player}
                isCurrentPlayer={false}
                isLandlord={false}
                cardCount={0}
              />
            ))}
          </div>

          {/* 游戏主区域 */}
          <GameBoard />
        </div>

        {/* 聊天面板 */}
        <ChatPanel />
      </div>
    </div>
  );
};

export default GameRoom;