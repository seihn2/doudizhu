import React, { useState, useEffect } from 'react';
import { Button, Card, Typography, Space, List, Tag, message, Spin } from 'antd';
import { ArrowLeftOutlined, UserOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const { Title } = Typography;

const RoomList = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 3000); // 每3秒刷新房间列表
    return () => clearInterval(interval);
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await axios.get('/api/rooms');
      setRooms(response.data);
    } catch (error) {
      console.error('获取房间列表失败:', error);
      message.error('获取房间列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = (roomId) => {
    navigate(`/game/${roomId}`);
  };

  const handleBack = () => {
    navigate('/');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'waiting':
        return 'blue';
      case 'playing':
        return 'green';
      case 'finished':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'waiting':
        return '等待中';
      case 'playing':
        return '游戏中';
      case 'finished':
        return '已结束';
      default:
        return '未知';
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <Card
          style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: '20px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
          }}
          bordered={false}
        >
          <div style={{ marginBottom: 20 }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={handleBack}
              style={{ marginBottom: 16 }}
            >
              返回首页
            </Button>

            <Title level={2} style={{ margin: 0, color: '#667eea' }}>
              🏠 房间列表
            </Title>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <Spin size="large" />
              <p style={{ marginTop: 16 }}>加载房间列表中...</p>
            </div>
          ) : (
            <List
              dataSource={rooms}
              locale={{
                emptyText: (
                  <div style={{ padding: 40, textAlign: 'center' }}>
                    <p>暂无可用房间</p>
                    <Button type="link" onClick={handleBack}>
                      创建新房间
                    </Button>
                  </div>
                )
              }}
              renderItem={(room) => (
                <List.Item
                  actions={[
                    <Button
                      type="primary"
                      icon={<PlayCircleOutlined />}
                      onClick={() => handleJoinRoom(room.room_id)}
                      disabled={room.status === 'playing' || room.player_count >= 3}
                      style={{
                        background: room.status === 'playing' || room.player_count >= 3
                          ? undefined
                          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none'
                      }}
                    >
                      {room.status === 'playing' ? '游戏中' :
                       room.player_count >= 3 ? '房间已满' : '加入房间'}
                    </Button>
                  ]}
                  style={{
                    background: 'rgba(255, 255, 255, 0.5)',
                    marginBottom: 12,
                    borderRadius: 12,
                    padding: '16px 20px'
                  }}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <span style={{ fontSize: 16, fontWeight: 'bold' }}>
                          {room.room_name}
                        </span>
                        <Tag color={getStatusColor(room.status)}>
                          {getStatusText(room.status)}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Space>
                        <UserOutlined />
                        <span>{room.player_count}/3 人</span>
                        <span style={{ color: '#999' }}>
                          房间ID: {room.room_id}
                        </span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}

          <div style={{
            marginTop: 20,
            padding: 20,
            background: 'rgba(102, 126, 234, 0.1)',
            borderRadius: '15px',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0, color: '#666' }}>
              💡 提示：房间列表每3秒自动刷新
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default RoomList;