import React from 'react';

const GameCard = ({ card, selected, onClick, disabled = false, size = 'normal' }) => {
  const getSuitSymbol = (suit) => {
    switch (suit) {
      case 'hearts': return '♥';
      case 'diamonds': return '♦';
      case 'clubs': return '♣';
      case 'spades': return '♠';
      default: return '';
    }
  };

  const getSuitColor = (suit) => {
    return suit === 'hearts' || suit === 'diamonds' ? '#ff4d4f' : '#262626';
  };

  const getCardDisplay = (value) => {
    if (value === 11) return 'J';
    if (value === 12) return 'Q';
    if (value === 13) return 'K';
    if (value === 14) return 'A';
    if (value === 15) return '2';
    if (value === 16) return '小王';
    if (value === 17) return '大王';
    return value.toString();
  };

  const getCardSize = () => {
    switch (size) {
      case 'small':
        return { width: 35, height: 50, fontSize: 10 };
      case 'large':
        return { width: 70, height: 100, fontSize: 16 };
      default:
        return { width: 50, height: 70, fontSize: 12 };
    }
  };

  const cardSize = getCardSize();
  const isJoker = card.value >= 16;
  const suitColor = isJoker ? (card.value === 16 ? '#000' : '#ff4d4f') : getSuitColor(card.suit);

  return (
    <div
      onClick={disabled ? undefined : onClick}
      style={{
        width: cardSize.width,
        height: cardSize.height,
        border: selected ? '3px solid #1890ff' : '2px solid #333',
        borderRadius: '6px',
        background: selected ? '#e6f7ff' : 'white',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '2px',
        cursor: disabled ? 'default' : 'pointer',
        transition: 'all 0.2s ease',
        transform: selected ? 'translateY(-10px)' : 'translateY(0)',
        boxShadow: selected
          ? '0 6px 16px rgba(24, 144, 255, 0.4)'
          : '0 2px 8px rgba(0, 0, 0, 0.1)',
        opacity: disabled ? 0.7 : 1,
        fontSize: cardSize.fontSize,
        fontWeight: 'bold',
        color: suitColor,
        userSelect: 'none'
      }}
      onMouseEnter={(e) => {
        if (!disabled && !selected) {
          e.target.style.transform = 'translateY(-5px)';
          e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled && !selected) {
          e.target.style.transform = 'translateY(0)';
          e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
        }
      }}
    >
      <div style={{
        textAlign: 'center',
        lineHeight: 1.2
      }}>
        <div>{getCardDisplay(card.value)}</div>
        {!isJoker && (
          <div style={{ fontSize: cardSize.fontSize + 2 }}>
            {getSuitSymbol(card.suit)}
          </div>
        )}
      </div>
    </div>
  );
};

export default GameCard;