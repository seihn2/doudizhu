import React from 'react';
import { Card, Typography, Avatar, Tag, Space } from 'antd';
import { UserOutlined, CrownOutlined } from '@ant-design/icons';

const { Text } = Typography;

const PlayerArea = ({ player, isCurrentPlayer, isLandlord, cardCount, score = 0 }) => {
  return (
    <Card
      style={{
        background: isCurrentPlayer
          ? 'rgba(24, 144, 255, 0.1)'
          : 'rgba(255, 255, 255, 0.9)',
        borderRadius: '15px',
        border: isCurrentPlayer ? '2px solid #1890ff' : '1px solid #d9d9d9',
        backdropFilter: 'blur(10px)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}
      bodyStyle={{
        padding: '20px',
        textAlign: 'center',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}
    >
      <div style={{ marginBottom: 15 }}>
        <Avatar
          size={64}
          icon={<UserOutlined />}
          style={{
            background: isLandlord
              ? 'linear-gradient(135deg, #faad14 0%, #fa8c16 100%)'
              : isCurrentPlayer
              ? 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)'
              : '#f0f0f0',
            color: isLandlord || isCurrentPlayer ? 'white' : '#999'
          }}
        />
        {isLandlord && (
          <CrownOutlined
            style={{
              position: 'absolute',
              marginLeft: -20,
              marginTop: -10,
              fontSize: 20,
              color: '#faad14'
            }}
          />
        )}
      </div>

      <div style={{ marginBottom: 10 }}>
        <Text strong style={{ fontSize: 16, display: 'block' }}>
          {player}
        </Text>
        <Space direction="vertical" size="small" style={{ marginTop: 8 }}>
          {isLandlord && (
            <Tag color="gold" style={{ fontSize: 12 }}>
              地主
            </Tag>
          )}
          {isCurrentPlayer && (
            <Tag color="blue" style={{ fontSize: 12 }}>
              当前玩家
            </Tag>
          )}
        </Space>
      </div>

      <div style={{
        background: 'rgba(0, 0, 0, 0.05)',
        borderRadius: '10px',
        padding: '10px',
        marginTop: 'auto'
      }}>
        <Space direction="vertical" size="small">
          <Text type="secondary" style={{ fontSize: 12 }}>
            手牌: {cardCount} 张
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            得分: {score}
          </Text>
        </Space>
      </div>

      {/* 简化的手牌显示 */}
      {cardCount > 0 && (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: 10,
          gap: -5
        }}>
          {Array.from({ length: Math.min(cardCount, 8) }).map((_, index) => (
            <div
              key={index}
              style={{
                width: 15,
                height: 20,
                background: '#f0f0f0',
                border: '1px solid #d9d9d9',
                borderRadius: '2px',
                marginLeft: index > 0 ? -5 : 0,
                zIndex: 8 - index,
                transform: `rotate(${(index - 4) * 2}deg)`
              }}
            />
          ))}
          {cardCount > 8 && (
            <Text
              style={{
                fontSize: 10,
                color: '#999',
                marginLeft: 5,
                alignSelf: 'center'
              }}
            >
              +{cardCount - 8}
            </Text>
          )}
        </div>
      )}
    </Card>
  );
};

export default PlayerArea;