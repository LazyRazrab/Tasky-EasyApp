import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Rich Text Editor Component
const RichTextEditor = ({ value, onChange, placeholder }) => {
  const [content, setContent] = useState(value || '');

  useEffect(() => {
    setContent(value || '');
  }, [value]);

  const handleChange = (e) => {
    const newContent = e.target.innerHTML;
    setContent(newContent);
    onChange(newContent);
  };

  const insertFormatting = (command, value = null) => {
    document.execCommand(command, false, value);
    document.getElementById('editor').focus();
  };

  return (
    <div className="rich-editor">
      <div className="editor-toolbar">
        <button 
          type="button"
          onClick={() => insertFormatting('bold')}
          className="toolbar-btn"
          title="Bold"
        >
          <strong>B</strong>
        </button>
        <button 
          type="button"
          onClick={() => insertFormatting('italic')}
          className="toolbar-btn"
          title="Italic"
        >
          <em>I</em>
        </button>
        <button 
          type="button"
          onClick={() => insertFormatting('underline')}
          className="toolbar-btn"
          title="Underline"
        >
          <u>U</u>
        </button>
        <button 
          type="button"
          onClick={() => insertFormatting('insertUnorderedList')}
          className="toolbar-btn"
          title="Bullet List"
        >
          •
        </button>
        <button 
          type="button"
          onClick={() => insertFormatting('insertOrderedList')}
          className="toolbar-btn"
          title="Numbered List"
        >
          1.
        </button>
        <button 
          type="button"
          onClick={() => insertFormatting('formatBlock', 'h2')}
          className="toolbar-btn"
          title="Heading"
        >
          H
        </button>
      </div>
      <div
        id="editor"
        className="editor-content"
        contentEditable
        dangerouslySetInnerHTML={{ __html: content }}
        onInput={handleChange}
        data-placeholder={placeholder}
      />
    </div>
  );
};

// Category Badge Component
const CategoryBadge = ({ category, small = false }) => {
  if (!category) return null;
  
  return (
    <span 
      className={`category-badge ${small ? 'category-badge-small' : ''}`}
      style={{ backgroundColor: category.color }}
    >
      {category.name}
    </span>
  );
};

// Tag Component
const Tag = ({ tag, onRemove, readonly = false }) => {
  return (
    <span className="tag">
      {tag}
      {!readonly && (
        <button 
          type="button"
          onClick={() => onRemove(tag)}
          className="tag-remove"
        >
          ×
        </button>
      )}
    </span>
  );
};

// Idea Card Component
const IdeaCard = ({ idea, categories, onEdit, onArchive, onDelete }) => {
  const category = categories.find(cat => cat.id === idea.category_id);
  
  return (
    <div className={`idea-card ${idea.is_archived ? 'idea-archived' : ''}`}>
      <div className="idea-card-header">
        <h3 className="idea-title">{idea.title}</h3>
        <div className="idea-actions">
          <button onClick={() => onEdit(idea)} className="btn-icon" title="Редактировать">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button onClick={() => onArchive(idea.id)} className="btn-icon" title={idea.is_archived ? "Разархивировать" : "Архивировать"}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l6 6 6-6" />
            </svg>
          </button>
          <button onClick={() => onDelete(idea.id)} className="btn-icon btn-danger" title="Удалить">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="idea-content" dangerouslySetInnerHTML={{ __html: idea.content }} />
      
      <div className="idea-meta">
        <div className="idea-tags">
          {idea.tags.map(tag => (
            <Tag key={tag} tag={tag} readonly />
          ))}
        </div>
        <CategoryBadge category={category} small />
      </div>
      
      <div className="idea-date">
        {new Date(idea.created_at).toLocaleDateString('ru-RU')}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [ideas, setIdeas] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingIdea, setEditingIdea] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  
  // Form states
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category_id: '',
    tags: []
  });
  const [categoryForm, setCategoryForm] = useState({
    name: '',
    color: '#6366f1'
  });
  const [tagInput, setTagInput] = useState('');

  // Fetch data
  const fetchIdeas = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory) params.append('category_id', selectedCategory);
      if (showArchived !== null) params.append('archived', showArchived);
      
      const response = await axios.get(`${API}/ideas?${params}`);
      setIdeas(response.data);
    } catch (error) {
      console.error('Error fetching ideas:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchIdeas();
    fetchCategories();
    fetchStats();
  }, [searchTerm, selectedCategory, showArchived]);

  // Form handlers
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingIdea) {
        await axios.put(`${API}/ideas/${editingIdea.id}`, formData);
      } else {
        await axios.post(`${API}/ideas`, formData);
      }
      setShowModal(false);
      resetForm();
      fetchIdeas();
      fetchStats();
    } catch (error) {
      console.error('Error saving idea:', error);
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/categories`, categoryForm);
      setShowCategoryModal(false);
      setCategoryForm({ name: '', color: '#6366f1' });
      fetchCategories();
      fetchStats();
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  const resetForm = () => {
    setFormData({ title: '', content: '', category_id: '', tags: [] });
    setEditingIdea(null);
    setTagInput('');
  };

  const openEditModal = (idea) => {
    setEditingIdea(idea);
    setFormData({
      title: idea.title,
      content: idea.content,
      category_id: idea.category_id || '',
      tags: idea.tags || []
    });
    setShowModal(true);
  };

  const handleArchive = async (ideaId) => {
    try {
      await axios.patch(`${API}/ideas/${ideaId}/archive`);
      fetchIdeas();
      fetchStats();
    } catch (error) {
      console.error('Error archiving idea:', error);
    }
  };

  const handleDelete = async (ideaId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту идею?')) {
      try {
        await axios.delete(`${API}/ideas/${ideaId}`);
        fetchIdeas();
        fetchStats();
      } catch (error) {
        console.error('Error deleting idea:', error);
      }
    }
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">💡 Журнал идей</h1>
          <div className="header-actions">
            <button 
              className="btn btn-secondary"
              onClick={() => setShowCategoryModal(true)}
            >
              + Категория
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => setShowModal(true)}
            >
              + Новая идея
            </button>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="stats-section">
        <div className="stats-container">
          <div className="stats-card stats-card-total">
            <div className="stats-number">{stats.total_ideas || 0}</div>
            <div className="stats-label">Всего идей</div>
          </div>
          <div className="stats-card stats-card-active">
            <div className="stats-number">{stats.active_ideas || 0}</div>
            <div className="stats-label">Активные</div>
          </div>
          <div className="stats-card stats-card-archived">
            <div className="stats-number">{stats.archived_ideas || 0}</div>
            <div className="stats-label">Архив</div>
          </div>
          <div className="stats-card stats-card-categories">
            <div className="stats-number">{stats.total_categories || 0}</div>
            <div className="stats-label">Категории</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filters-container">
          <div className="search-box">
            <input
              type="text"
              placeholder="Поиск идей..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="category-select"
          >
            <option value="">Все категории</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          <div className="archive-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={showArchived}
                onChange={(e) => setShowArchived(e.target.checked)}
                className="toggle-input"
              />
              <span className="toggle-slider"></span>
              <span className="toggle-text">Показать архив</span>
            </label>
          </div>
        </div>
      </div>

      {/* Ideas Grid */}
      <main className="main-content">
        <div className="ideas-grid">
          {ideas.length === 0 ? (
            <div className="empty-state">
              <p>Пока нет идей. Создайте первую!</p>
            </div>
          ) : (
            ideas.map(idea => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                categories={categories}
                onEdit={openEditModal}
                onArchive={handleArchive}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      </main>

      {/* Idea Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingIdea ? 'Редактировать идею' : 'Новая идея'}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>Название</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label>Категория</label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData(prev => ({...prev, category_id: e.target.value}))}
                  className="form-select"
                >
                  <option value="">Без категории</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Содержание</label>
                <RichTextEditor
                  value={formData.content}
                  onChange={(content) => setFormData(prev => ({...prev, content}))}
                  placeholder="Опишите вашу идею..."
                />
              </div>

              <div className="form-group">
                <label>Теги</label>
                <div className="tags-input-container">
                  <div className="tags-display">
                    {formData.tags.map(tag => (
                      <Tag key={tag} tag={tag} onRemove={removeTag} />
                    ))}
                  </div>
                  <div className="tag-input-group">
                    <input
                      type="text"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      placeholder="Добавить тег"
                      className="tag-input"
                    />
                    <button type="button" onClick={addTag} className="btn btn-sm">
                      Добавить
                    </button>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Отмена
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingIdea ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Category Modal */}
      {showCategoryModal && (
        <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
          <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Новая категория</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCategoryModal(false)}
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleCategorySubmit} className="modal-form">
              <div className="form-group">
                <label>Название</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm(prev => ({...prev, name: e.target.value}))}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label>Цвет</label>
                <input
                  type="color"
                  value={categoryForm.color}
                  onChange={(e) => setCategoryForm(prev => ({...prev, color: e.target.value}))}
                  className="form-color"
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowCategoryModal(false)} className="btn btn-secondary">
                  Отмена
                </button>
                <button type="submit" className="btn btn-primary">
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;