import React from 'react';
import { Card, Typography, Button, Space } from 'antd';
import { ClearOutlined } from '@ant-design/icons';
import useGameStore from '../store/gameStore';
import GameCard from './GameCard';

const { Text } = Typography;

const PlayerCards = () => {
  const {
    handCards,
    selectedCards,
    toggleCardSelection,
    clearSelectedCards,
    playerName
  } = useGameStore();

  const handleCardClick = (cardIndex) => {
    toggleCardSelection(cardIndex);
  };

  const handleClearSelection = () => {
    clearSelectedCards();
  };

  if (!handCards || handCards.length === 0) {
    return null;
  }

  return (
    <Card
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px 20px 0 0',
        border: 'none',
        borderTop: '1px solid #d9d9d9',
        zIndex: 1000
      }}
    >
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 15
      }}>
        <Space>
          <Text strong style={{ fontSize: 16 }}>
            {playerName} 的手牌 ({handCards.length}张)
          </Text>
          {selectedCards.length > 0 && (
            <Text type="secondary">
              已选择 {selectedCards.length} 张牌
            </Text>
          )}
        </Space>

        {selectedCards.length > 0 && (
          <Button
            size="small"
            icon={<ClearOutlined />}
            onClick={handleClearSelection}
          >
            清空选择
          </Button>
        )}
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-end',
        overflowX: 'auto',
        padding: '10px 0',
        gap: 2
      }}>
        {handCards.map((card, index) => (
          <GameCard
            key={`${card.value}-${card.suit}-${index}`}
            card={card}
            selected={selectedCards.includes(index)}
            onClick={() => handleCardClick(index)}
            size="normal"
          />
        ))}
      </div>

      {selectedCards.length > 0 && (
        <div style={{
          textAlign: 'center',
          marginTop: 10,
          padding: '10px 0',
          borderTop: '1px solid #f0f0f0'
        }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            💡 提示：再次点击卡牌可取消选择，选好后点击"出牌"按钮
          </Text>
        </div>
      )}
    </Card>
  );
};

export default PlayerCards;