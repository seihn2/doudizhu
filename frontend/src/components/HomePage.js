import React, { useState } from 'react';
import { Button, Input, Card, Typography, Space, message } from 'antd';
import { UserOutlined, HomeOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  const [playerName, setPlayerName] = useState('');
  const [roomId, setRoomId] = useState('');
  const navigate = useNavigate();
  const setPlayerInfo = useGameStore(state => state.setPlayerInfo);

  const handleQuickStart = () => {
    if (!playerName.trim()) {
      message.error('请输入玩家名称');
      return;
    }

    setPlayerInfo(playerName, Math.random().toString(36).substr(2, 9));

    // 生成随机房间ID
    const randomRoomId = 'room_' + Math.random().toString(36).substr(2, 6);
    navigate(`/game/${randomRoomId}`);
  };

  const handleJoinRoom = () => {
    if (!playerName.trim()) {
      message.error('请输入玩家名称');
      return;
    }

    if (!roomId.trim()) {
      message.error('请输入房间ID');
      return;
    }

    setPlayerInfo(playerName, Math.random().toString(36).substr(2, 9));
    navigate(`/game/${roomId}`);
  };

  const handleViewRooms = () => {
    navigate('/rooms');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 500,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}
        bordered={false}
      >
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <Title level={1} style={{ color: '#667eea', marginBottom: 8 }}>
            🃏 AI斗地主
          </Title>
          <Paragraph style={{ fontSize: 16, color: '#666' }}>
            与AI对手一较高下，体验经典斗地主游戏
          </Paragraph>
        </div>

        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Input
            size="large"
            placeholder="请输入您的玩家名称"
            prefix={<UserOutlined />}
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            onPressEnter={handleQuickStart}
            style={{ borderRadius: '10px' }}
          />

          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={handleQuickStart}
            style={{
              width: '100%',
              height: 50,
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              fontSize: 16,
              fontWeight: 'bold'
            }}
          >
            快速开始
          </Button>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            margin: '20px 0',
            color: '#999'
          }}>
            <div style={{ flex: 1, height: 1, background: '#e0e0e0' }}></div>
            <span style={{ margin: '0 15px' }}>或</span>
            <div style={{ flex: 1, height: 1, background: '#e0e0e0' }}></div>
          </div>

          <Input
            size="large"
            placeholder="输入房间ID"
            prefix={<HomeOutlined />}
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            onPressEnter={handleJoinRoom}
            style={{ borderRadius: '10px' }}
          />

          <Button
            size="large"
            onClick={handleJoinRoom}
            style={{
              width: '100%',
              height: 50,
              borderRadius: '10px',
              fontSize: 16
            }}
          >
            加入房间
          </Button>

          <Button
            size="large"
            onClick={handleViewRooms}
            style={{
              width: '100%',
              height: 50,
              borderRadius: '10px',
              fontSize: 16
            }}
          >
            房间列表
          </Button>
        </Space>

        <div style={{
          marginTop: 30,
          padding: 20,
          background: 'rgba(102, 126, 234, 0.1)',
          borderRadius: '15px',
          textAlign: 'center'
        }}>
          <Paragraph style={{ margin: 0, color: '#666' }}>
            💡 游戏特色：智能AI对手、实时对战、精美界面
          </Paragraph>
        </div>
      </Card>
    </div>
  );
};

export default HomePage;