import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Typography, Space } from 'antd';
import { SendOutlined, MessageOutlined } from '@ant-design/icons';
import useGameStore from '../store/gameStore';

const { Text } = Typography;
const { TextArea } = Input;

const ChatPanel = () => {
  const [message, setMessage] = useState('');
  const [collapsed, setCollapsed] = useState(false);
  const messagesEndRef = useRef(null);

  const {
    chatMessages,
    sendChatMessage,
    playerName
  } = useGameStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSendMessage = () => {
    if (message.trim()) {
      sendChatMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card
      style={{
        height: '100%',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        display: 'flex',
        flexDirection: 'column'
      }}
      bodyStyle={{
        padding: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
      title={
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer'
          }}
          onClick={() => setCollapsed(!collapsed)}
        >
          <Space>
            <MessageOutlined />
            <span>聊天室</span>
          </Space>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {collapsed ? '展开' : '收起'}
          </Text>
        </div>
      }
    >
      {!collapsed && (
        <>
          {/* 消息列表 */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0 16px',
            maxHeight: 'calc(100vh - 250px)'
          }}>
            <List
              dataSource={chatMessages}
              locale={{
                emptyText: (
                  <div style={{
                    textAlign: 'center',
                    color: '#999',
                    padding: '40px 0'
                  }}>
                    <MessageOutlined style={{ fontSize: 24, marginBottom: 8 }} />
                    <div>暂无聊天消息</div>
                    <div style={{ fontSize: 12 }}>开始聊天吧！</div>
                  </div>
                )
              }}
              renderItem={(item) => (
                <List.Item
                  style={{
                    border: 'none',
                    padding: '8px 0',
                    flexDirection: 'column',
                    alignItems: 'flex-start'
                  }}
                >
                  <div style={{
                    background: item.player_name === playerName
                      ? 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)'
                      : '#f5f5f5',
                    color: item.player_name === playerName ? 'white' : '#333',
                    padding: '8px 12px',
                    borderRadius: '12px',
                    maxWidth: '80%',
                    alignSelf: item.player_name === playerName ? 'flex-end' : 'flex-start',
                    wordBreak: 'break-word'
                  }}>
                    {item.player_name !== playerName && (
                      <div style={{
                        fontSize: 12,
                        opacity: 0.8,
                        marginBottom: 4
                      }}>
                        {item.player_name}
                      </div>
                    )}
                    <div>{item.message}</div>
                    <div style={{
                      fontSize: 10,
                      opacity: 0.7,
                      marginTop: 4,
                      textAlign: 'right'
                    }}>
                      {formatTime(item.timestamp)}
                    </div>
                  </div>
                </List.Item>
              )}
            />
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div style={{
            borderTop: '1px solid #f0f0f0',
            padding: 16
          }}>
            <div style={{
              display: 'flex',
              gap: 8
            }}>
              <TextArea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入消息..."
                autoSize={{ minRows: 1, maxRows: 3 }}
                style={{
                  flex: 1,
                  resize: 'none'
                }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                disabled={!message.trim()}
                style={{
                  background: message.trim()
                    ? 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)'
                    : undefined,
                  border: 'none'
                }}
              />
            </div>

            {/* 快捷消息 */}
            <div style={{
              marginTop: 8,
              display: 'flex',
              gap: 4,
              flexWrap: 'wrap'
            }}>
              {['好牌！', '不要！', '快点！', '666'].map((quickMsg) => (
                <Button
                  key={quickMsg}
                  size="small"
                  onClick={() => {
                    sendChatMessage(quickMsg);
                  }}
                  style={{
                    fontSize: 12,
                    height: 24
                  }}
                >
                  {quickMsg}
                </Button>
              ))}
            </div>
          </div>
        </>
      )}
    </Card>
  );
};

export default ChatPanel;