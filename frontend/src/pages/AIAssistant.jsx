
import { useEffect, useRef, useState } from "react";
import api from "../services/api";
import "./AIAssistant.css";

function getErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (!error.response) {
    return "Cannot connect to the backend. Check that FastAPI is running on port 8000.";
  }

  return "Something went wrong. Please try again.";
}

function getCitationLabel(source, index) {
  if (typeof source === "string") {
    return source;
  }

  if (source && typeof source === "object") {
    return (
      source.title ||
      source.source ||
      source.filename ||
      source.file ||
      source.name ||
      `Source ${index + 1}`
    );
  }

  return `Source ${index + 1}`;
}

function AIAssistant() {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, sending]);

  async function loadConversations() {
    setLoadingConversations(true);

    try {
      const response = await api.get("/chat/conversations");
      setConversations(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoadingConversations(false);
    }
  }

  function startNewConversation() {
    setActiveConversation(null);
    setMessages([]);
    setQuestion("");
    setError("");
    inputRef.current?.focus();
  }

  async function openConversation(conversation) {
    if (sending) return;

    setActiveConversation(conversation);
    setMessages([]);
    setError("");
    setLoadingMessages(true);

    try {
      const response = await api.get(
        `/chat/conversations/${conversation.id}/messages`
      );

      setMessages(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoadingMessages(false);
    }
  }

  async function sendMessage(event) {
    event.preventDefault();

    const text = question.trim();

    if (!text || sending || loadingMessages) return;

    setQuestion("");
    setError("");
    setSending(true);

    const temporaryId = `temp-${Date.now()}`;

    setMessages((previous) => [
      ...previous,
      {
        id: temporaryId,
        role: "user",
        content: text,
      },
    ]);

    try {
      let conversation = activeConversation;

      if (!conversation) {
        const created = await api.post("/chat/conversations", {
          title: text.slice(0, 200),
        });

        conversation = created.data;
        setActiveConversation(conversation);
      }

      const response = await api.post(
        `/chat/conversations/${conversation.id}/messages`,
        { question: text }
      );

      const data = response.data;

      setMessages((previous) => [
        ...previous.filter((message) => message.id !== temporaryId),
        {
          ...data.question,
          citations: [],
        },
        {
          ...data.answer,
          citations: data.citations || [],
          retrieval_status: data.retrieval_status,
        },
      ]);

      await loadConversations();
    } catch (err) {
      setMessages((previous) =>
        previous.filter((message) => message.id !== temporaryId)
      );

      setQuestion(text);
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  return (
    <section className="ai-assistant">
      <aside className="chat-sidebar">
        <button
          type="button"
          className="new-chat-button"
          onClick={startNewConversation}
          disabled={sending}
        >
          <span>＋</span> New conversation
        </button>

        <h3 className="conversation-heading">
          Recent conversations
        </h3>

        <div className="conversation-list">
          {loadingConversations ? (
            <p className="conversation-empty">Loading chats...</p>
          ) : conversations.length === 0 ? (
            <p className="conversation-empty">
              Your conversations will appear here.
            </p>
          ) : (
            conversations.map((conversation) => (
              <button
                type="button"
                key={conversation.id}
                className={`conversation-item ${
                  activeConversation?.id === conversation.id
                    ? "selected"
                    : ""
                }`}
                onClick={() => openConversation(conversation)}
                disabled={sending}
                title={conversation.title}
              >
                <span className="conversation-icon">💬</span>
                <span className="conversation-title">
                  {conversation.title}
                </span>
              </button>
            ))
          )}
        </div>

        <div className="chat-sidebar-note">
          <span>🌱</span>
          <p>
            Ask questions about crops, soil, plant diseases,
            fertilizers, and irrigation.
          </p>
        </div>
      </aside>

      <div className="chat-main">
        <header className="chat-header">
          <div className="assistant-avatar">🌿</div>
          <div>
            <h2>AI Agriculture Assistant</h2>
            <p>Smart farming guidance powered by agricultural RAG</p>
          </div>
        </header>

        <div className="chat-messages">
          {messages.length === 0 && !loadingMessages ? (
            <div className="chat-welcome">
              <div className="welcome-icon">🌱</div>
              <h2>How can I help your farm today?</h2>
              <p>
                Ask a question to get agricultural guidance from
                your AI assistant.
              </p>

              <div className="suggested-questions">
                {[
                  "How can I improve rice crop growth?",
                  "How do I improve soil health?",
                  "What causes yellow leaves on plants?",
                  "How should I plan irrigation before rainfall?",
                ].map((suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    onClick={() => setQuestion(suggestion)}
                    disabled={sending}
                  >
                    {suggestion}
                    <span>↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`chat-message ${
                    message.role === "user" ? "user-message" : "ai-message"
                  }`}
                >
                  {message.role !== "user" && (
                    <div className="message-avatar">🌿</div>
                  )}

                  <div className="message-content">
                    <span className="message-role">
                      {message.role === "user" ? "You" : "AI Assistant"}
                    </span>

                    <div className="message-bubble">
                      {message.content}
                    </div>

                    {message.role !== "user" &&
                      Array.isArray(message.citations) &&
                      message.citations.length > 0 && (
                        <div className="citation-list">
                          <strong>📚 Sources</strong>
                          {message.citations.map((source, index) => (
                            <div
                              className="citation-item"
                              key={`${getCitationLabel(source, index)}-${index}`}
                            >
                              {getCitationLabel(source, index)}
                            </div>
                          ))}
                        </div>
                      )}
                  </div>
                </article>
              ))}

              {sending && (
                <div className="typing-indicator">
                  <span className="message-avatar">🌿</span>
                  <div>
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <p>Preparing your agricultural guidance...</p>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {loadingMessages && (
            <div className="chat-loading">Loading conversation...</div>
          )}
        </div>

        {error && (
          <div className="chat-error" role="alert">
            <span>{error}</span>
            <button
              type="button"
              onClick={() => setError("")}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        <form className="chat-composer" onSubmit={sendMessage}>
          <textarea
            ref={inputRef}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            placeholder="Ask an agricultural question..."
            rows={2}
            maxLength={5000}
            disabled={sending || loadingMessages}
            aria-label="Your agricultural question"
          />

          <div className="composer-footer">
            <span>Enter to send · Shift + Enter for a new line</span>
            <button
              type="submit"
              className="send-message-button"
              disabled={!question.trim() || sending || loadingMessages}
            >
              {sending ? "Thinking..." : "Send ↑"}
            </button>
          </div>
        </form>

        <p className="chat-disclaimer">
          AI-generated advice is for guidance. Verify important
          agricultural decisions with local agricultural experts.
        </p>
      </div>
    </section>
  );
}

export default AIAssistant;
