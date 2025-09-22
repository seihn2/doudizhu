import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Button, message, Space, Tag } from 'antd';
import { ArrowLeftOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import useGameStore from '../store/gameStore';
import GameBoard from './GameBoard';
import PlayerArea from './PlayerArea';
import useSingleGameLogic from '../hooks/useSingleGameLogic';

const { Title, Text } = Typography;

const SingleGame = () => {
  const navigate = useNavigate();
  const { playerName } = useGameStore();
  const [gameStarted, setGameStarted] = useState(false);

  const {
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
  } = useSingleGameLogic();

  useEffect(() => {
    if (!playerName) {
      message.error('请先设置玩家名称');
      navigate('/');
      return;
    }

    // 自动开始游戏
    const timer = setTimeout(async () => {
      await startGame(playerName);
      setGameStarted(true);
    }, 1000);

    return () => {
      clearTimeout(timer);
      cleanup();
    };
  }, [playerName, navigate, startGame, cleanup]);

  const handleBack = () => {
    navigate('/');
  };

  const handlePlayCards = async (selectedCardIndices) => {
    if (!isMyTurn || selectedCardIndices.length === 0 || loading) return;

    const cardsToPlay = selectedCardIndices.map(index => myCards[index]);
    const success = await playCards(cardsToPlay);

    if (!success) {
      message.error('无效的出牌！');
    }
  };

  const handlePass = async () => {
    if (!isMyTurn || loading) return;
    const success = await pass();

    if (!success) {
      message.error('过牌失败！');
    }
  };

  if (!gameStarted || !gameId) {
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
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
            style={{ position: 'absolute', top: 20, left: 20 }}
          >
            返回
          </Button>

          <Title level={2} style={{ color: '#667eea', marginBottom: 30 }}>
            🎮 正在准备游戏...
          </Title>

          <Space direction="vertical" size="large">
            <div>
              <Text strong style={{ fontSize: 16 }}>玩家：{playerName}</Text>
            </div>

            <div style={{
              background: 'rgba(102, 126, 234, 0.1)',
              borderRadius: '15px',
              padding: 20
            }}>
              <Title level={4} style={{ margin: 0, marginBottom: 15 }}>
                AI对手准备中...
              </Title>
              <Space>
                <Tag icon={<RobotOutlined />} color="blue">AI玩家1</Tag>
                <Tag icon={<RobotOutlined />} color="green">AI玩家2</Tag>
              </Space>
            </div>

            <Text type="secondary">发牌中，请稍候...</Text>
          </Space>
        </Card>
      </div>
    );
  }

  if (isGameOver) {
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
          padding: 40,
          maxWidth: 500
        }}>
          <Title level={2} style={{
            color: winner?.name === playerName ? '#52c41a' : '#ff4d4f',
            marginBottom: 30
          }}>
            🎉 游戏结束！
          </Title>

          <div style={{ marginBottom: 30 }}>
            <Text style={{ fontSize: 18 }}>
              {winner?.name === playerName ? '🎊 恭喜你获胜！' : `😔 ${winner?.name} 获胜`}
            </Text>
          </div>

          <Space>
            <Button
              type="primary"
              onClick={() => window.location.reload()}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none'
              }}
            >
              再来一局
            </Button>
            <Button onClick={handleBack}>
              返回首页
            </Button>
          </Space>
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
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        padding: 20,
        paddingTop: 70
      }}>
        {/* AI玩家区域 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 20,
          marginBottom: 20,
          height: '200px'
        }}>
          <PlayerArea
            player="AI玩家1"
            isCurrentPlayer={currentPlayer === 1}
            isLandlord={gameState?.landlord_idx === 1}
            cardCount={getAIPlayerCards(1)}
            score={0}
          />
          <PlayerArea
            player="AI玩家2"
            isCurrentPlayer={currentPlayer === 2}
            isLandlord={gameState?.landlord_idx === 2}
            cardCount={getAIPlayerCards(2)}
            score={0}
          />
        </div>

        {/* 游戏主区域 */}
        <SingleGameBoard
          gameState={gameState}
          myCards={myCards}
          lastPlay={lastPlay}
          playHistory={playHistory}
          isMyTurn={isMyTurn}
          currentPlayer={currentPlayer}
          playerName={playerName}
          loading={loading}
          onPlayCards={handlePlayCards}
          onPass={handlePass}
        />
      </div>
    </div>
  );
};

// 单人游戏面板组件
const SingleGameBoard = ({
  gameState,
  myCards,
  lastPlay,
  playHistory,
  isMyTurn,
  currentPlayer,
  playerName,
  loading,
  onPlayCards,
  onPass
}) => {
  const [selectedCards, setSelectedCards] = useState([]);
  const [pendingRemoveCards, setPendingRemoveCards] = useState([]);

  const handleCardClick = (cardIndex) => {
    setSelectedCards(prev => {
      const newSelected = [...prev];
      const index = newSelected.indexOf(cardIndex);

      if (index > -1) {
        newSelected.splice(index, 1);
      } else {
        newSelected.push(cardIndex);
      }

      return newSelected;
    });
  };

  const handlePlayCardsClick = async () => {
    if (selectedCards.length === 0 || loading) return;

    // 立即将选中的牌移到待移除状态，提供即时反馈
    const cardsToRemove = selectedCards.map(index => myCards[index]);
    setPendingRemoveCards(cardsToRemove);
    setSelectedCards([]);

    try {
      await onPlayCards(selectedCards);
      // 成功后清空待移除卡牌（后端已更新手牌）
      setPendingRemoveCards([]);
    } catch (error) {
      // 如果出牌失败，恢复卡牌
      setPendingRemoveCards([]);
      console.error('出牌失败:', error);
    }
  };

  const handlePassClick = async () => {
    if (loading) return;
    await onPass();
    setSelectedCards([]);
  };

  const getCurrentPlayerName = () => {
    if (currentPlayer === 0) return playerName;
    return `AI玩家${currentPlayer}`;
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
            <Text strong>回合: {gameState?.round_count || 0}</Text>
            <Text>阶段: 游戏进行中</Text>
            {gameState?.landlord_idx !== null && (
              <Tag color="gold">
                地主: {gameState.landlord_idx === 0 ? playerName : `AI玩家${gameState.landlord_idx}`}
              </Tag>
            )}
          </Space>

          <Space>
            <Text>当前玩家: {getCurrentPlayerName()}</Text>
            {isMyTurn && (
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
          {/* 出牌历史显示 */}
          {playHistory && playHistory.length > 0 ? (
            <div style={{ textAlign: 'center', marginBottom: 30, width: '100%' }}>
              <Title level={4} style={{ marginBottom: 20 }}>
                📝 最近出牌记录
              </Title>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 15,
                maxWidth: 600,
                margin: '0 auto'
              }}>
                {playHistory.slice().reverse().map((history, index) => (
                  <div
                    key={index}
                    style={{
                      background: 'rgba(255, 255, 255, 0.8)',
                      borderRadius: '12px',
                      padding: '15px',
                      border: '1px solid #e0e0e0'
                    }}
                  >
                    <div style={{ marginBottom: 10 }}>
                      <Text strong style={{ fontSize: 14 }}>
                        {history.player_name}：
                      </Text>
                      <Text style={{ color: '#666', marginLeft: 8 }}>
                        {history.action_type.includes('过牌') ? '过牌' : '出牌'}
                      </Text>
                    </div>

                    {history.cards && history.cards.length > 0 && (
                      <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        gap: 3,
                        flexWrap: 'wrap'
                      }}>
                        {history.cards.map((card, cardIndex) => (
                          <div
                            key={cardIndex}
                            style={{
                              width: 35,
                              height: 50,
                              border: '1px solid #333',
                              borderRadius: '4px',
                              background: 'white',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 10,
                              fontWeight: 'bold',
                              color: card.suit === 'hearts' || card.suit === 'diamonds' ? '#ff4d4f' : '#262626'
                            }}
                          >
                            {card.value === 16 ? '小王' : card.value === 17 ? '大王' :
                             card.value === 14 ? 'A' : card.value === 15 ? '2' :
                             card.value === 11 ? 'J' : card.value === 12 ? 'Q' :
                             card.value === 13 ? 'K' : card.value}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#999' }}>
              <Title level={3} style={{ color: '#999' }}>
                🃏 开始出牌
              </Title>
              <p>选择要出的牌，点击出牌按钮</p>
            </div>
          )}
        </div>

        {/* 游戏操作按钮 */}
        {isMyTurn && (
          <div style={{
            borderTop: '1px solid #f0f0f0',
            padding: '20px 0',
            textAlign: 'center'
          }}>
            <Space size="large">
              <Button
                type="primary"
                size="large"
                onClick={handlePlayCardsClick}
                disabled={selectedCards.length === 0 || loading}
                loading={loading}
                style={{
                  background: selectedCards.length > 0 && !loading
                    ? 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)'
                    : undefined,
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0 30px',
                  height: 45
                }}
              >
                {loading ? '出牌中...' : `出牌 (${selectedCards.length})`}
              </Button>

              <Button
                size="large"
                onClick={handlePassClick}
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

      {/* 玩家手牌 */}
      {myCards && myCards.length > 0 && (
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
            <Text strong style={{ fontSize: 16 }}>
              {playerName} 的手牌 ({myCards.length}张)
            </Text>
            {selectedCards.length > 0 && (
              <Text type="secondary">
                已选择 {selectedCards.length} 张牌
              </Text>
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
            {myCards.map((card, index) => {
              // 检查这张牌是否在待移除列表中
              const isPendingRemoval = pendingRemoveCards.some(removeCard =>
                removeCard.value === card.value && removeCard.suit === card.suit
              );

              return (
                <div
                  key={`${card.value}-${card.suit}-${index}`}
                  onClick={() => !isPendingRemoval && handleCardClick(index)}
                  style={{
                    width: 50,
                    height: 70,
                    border: selectedCards.includes(index) ? '3px solid #1890ff' : '2px solid #333',
                    borderRadius: '6px',
                    background: selectedCards.includes(index) ? '#e6f7ff' : 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '2px',
                    cursor: isPendingRemoval ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s ease',
                    transform: selectedCards.includes(index) ? 'translateY(-10px)' : 'translateY(0)',
                    fontSize: 12,
                    fontWeight: 'bold',
                    color: card.suit === 'hearts' || card.suit === 'diamonds' ? '#ff4d4f' : '#262626',
                    opacity: isPendingRemoval ? 0.3 : 1,
                    filter: isPendingRemoval ? 'grayscale(100%)' : 'none'
                  }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <div>
                      {card.value === 16 ? '小王' : card.value === 17 ? '大王' :
                       card.value === 14 ? 'A' : card.value === 15 ? '2' :
                       card.value === 11 ? 'J' : card.value === 12 ? 'Q' :
                       card.value === 13 ? 'K' : card.value}
                    </div>
                    {card.value < 16 && (
                      <div style={{ fontSize: 14 }}>
                        {card.suit === 'hearts' ? '♥' :
                         card.suit === 'diamonds' ? '♦' :
                         card.suit === 'clubs' ? '♣' : '♠'}
                      </div>
                    )}
                  </div>
                  {isPendingRemoval && (
                    <div style={{
                      position: 'absolute',
                      background: 'rgba(0,0,0,0.7)',
                      color: 'white',
                      fontSize: 8,
                      padding: '2px 4px',
                      borderRadius: '2px',
                      top: -10,
                      left: '50%',
                      transform: 'translateX(-50%)'
                    }}>
                      出牌中
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
};

export default SingleGame;