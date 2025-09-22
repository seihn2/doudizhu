import React from 'react';
import { Card, Button, Space, Typography, Tag } from 'antd';
import { PlayCircleOutlined, StopOutlined } from '@ant-design/icons';
import useGameStore from '../store/gameStore';
import GameCard from './GameCard';
import PlayerCards from './PlayerCards';

const { Title, Text } = Typography;

const GameBoard = () => {
  const {
    gamePhase,
    currentPlayerIdx,
    landlordIdx,
    players,
    playerName,
    lastPlay,
    lastPlayerIdx,
    passCount,
    roundCount,
    playCards,
    pass,
    selectedCards
  } = useGameStore();

  const isMyTurn = () => {
    const myIndex = players.findIndex(p => p === playerName);
    return myIndex === currentPlayerIdx;
  };

  const handlePlayCards = () => {
    if (selectedCards.length === 0) return;
    playCards();
  };

  const handlePass = () => {
    pass();
  };

  const getPlayerName = (index) => {
    return players[index] || `玩家${index + 1}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 游戏信息栏 */}
      <Card style={{
        background: 'rgba(255, 255, 255, 0.9)',
        borderRadius: '15px',
        marginBottom: 20,
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Space>
            <Text strong>回合: {roundCount}</Text>
            <Text>阶段: {gamePhase === 'playing' ? '游戏进行中' : '等待中'}</Text>
            {landlordIdx !== null && (
              <Tag color="gold">地主: {getPlayerName(landlordIdx)}</Tag>
            )}
          </Space>

          <Space>
            <Text>当前玩家: {getPlayerName(currentPlayerIdx)}</Text>
            {isMyTurn() && (
              <Tag color="blue">轮到你了!</Tag>
            )}
          </Space>
        </div>
      </Card>

      {/* 中央游戏区域 */}
      <Card style={{
        flex: 1,
        background: 'rgba(255, 255, 255, 0.9)',
        borderRadius: '20px',
        display: 'flex',
        flexDirection: 'column',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 300
        }}>
          {/* 上一手牌显示 */}
          {lastPlay && lastPlay.cards && lastPlay.cards.length > 0 ? (
            <div style={{ textAlign: 'center', marginBottom: 30 }}>
              <Title level={4} style={{ marginBottom: 15 }}>
                {getPlayerName(lastPlayerIdx)} 出牌:
              </Title>
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: 5,
                marginBottom: 10
              }}>
                {lastPlay.cards.map((card, index) => (
                  <GameCard
                    key={index}
                    card={card}
                    selected={false}
                    onClick={() => {}}
                    disabled={true}
                  />
                ))}
              </div>
              {lastPlay.card_type && (
                <Tag color="green">{lastPlay.card_type}</Tag>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#999' }}>
              <Title level={3} style={{ color: '#999' }}>
                🃏 等待出牌
              </Title>
              <p>选择要出的牌，点击出牌按钮</p>
            </div>
          )}

          {/* 过牌信息 */}
          {passCount > 0 && (
            <div style={{ textAlign: 'center', marginTop: 20 }}>
              <Text type="secondary">
                连续过牌: {passCount} 次
                {passCount >= 2 && ' (即将清空上一手牌)'}
              </Text>
            </div>
          )}
        </div>

        {/* 游戏操作按钮 */}
        {isMyTurn() && gamePhase === 'playing' && (
          <div style={{
            borderTop: '1px solid #f0f0f0',
            padding: '20px 0',
            textAlign: 'center'
          }}>
            <Space size="large">
              <Button
                type="primary"
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={handlePlayCards}
                disabled={selectedCards.length === 0}
                style={{
                  background: selectedCards.length > 0
                    ? 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)'
                    : undefined,
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0 30px',
                  height: 45
                }}
              >
                出牌 ({selectedCards.length})
              </Button>

              <Button
                size="large"
                icon={<StopOutlined />}
                onClick={handlePass}
                style={{
                  borderRadius: '10px',
                  padding: '0 30px',
                  height: 45
                }}
              >
                过牌
              </Button>
            </Space>
          </div>
        )}
      </Card>

      {/* 当前玩家手牌区域 */}
      <PlayerCards />
    </div>
  );
};

export default GameBoard;