/**
 * Grandma's Recipe Archive - Client-side JavaScript
 * Handles recipe loading, search, filtering, and navigation
 */

// =============================================================================
// Security Utilities - XSS Prevention
// =============================================================================

/**
 * Escape HTML special characters to prevent XSS attacks.
 * Always use this when inserting dynamic content into innerHTML.
 * @param {*} text - The text to escape (will be converted to string)
 * @returns {string} - HTML-escaped string safe for innerHTML
 */
function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}

/**
 * Sanitize URLs to prevent javascript: and data: XSS attacks.
 * Only allows relative paths, http://, and https:// URLs.
 * @param {string} url - The URL to sanitize
 * @returns {string} - Sanitized URL or '#' if unsafe
 */
function sanitizeUrl(url) {
  if (!url) return '#';
  const trimmed = String(url).trim();
  // Allow relative paths and http(s) URLs only
  if (trimmed.startsWith('/') ||
      trimmed.startsWith('./') ||
      trimmed.startsWith('../') ||
      trimmed.startsWith('http://') ||
      trimmed.startsWith('https://')) {
    return trimmed;
  }
  // Allow simple filenames and paths (no protocol)
  if (/^[a-zA-Z0-9_\-./]+$/.test(trimmed) && !trimmed.includes(':')) {
    return trimmed;
  }
  return '#';
}

/**
 * Escape a value for use in an HTML attribute.
 * @param {*} value - The value to escape
 * @returns {string} - Escaped string safe for attribute values
 */
function escapeAttr(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// =============================================================================
// Application Code
// =============================================================================

// Global state
let recipes = [];
let categories = new Set();
let allTags = new Set();
let currentFilter = { search: '', category: '', tag: '', collection: '' };
let showMetric = false; // Toggle for metric conversions

// DOM Ready
document.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadRecipes();
  setupEventListeners();
  handleRouting();
}

/**
 * Load recipes from JSON file
 */
async function loadRecipes() {
  try {
    const response = await fetch('data/recipes_master.json');
    const data = await response.json();
    recipes = data.recipes || [];

    // Extract categories and tags
    recipes.forEach(recipe => {
      if (recipe.category) categories.add(recipe.category);
      if (recipe.tags) recipe.tags.forEach(tag => allTags.add(tag));
    });

    console.log(`Loaded ${recipes.length} recipes`);
    updateCollectionCounts();
  } catch (error) {
    console.error('Failed to load recipes:', error);
    showError('Unable to load recipes. Please refresh the page.');
  }
}

/**
 * Update collection filter buttons with recipe counts
 */
function updateCollectionCounts() {
  const collectionFilters = document.getElementById('collection-filters');
  if (!collectionFilters) return;

  // Count recipes by collection (excluding reference collection from individual counts)
  const counts = {
    '': recipes.length, // All recipes
    'grandma': 0,
    'mommom': 0,
    'granny': 0
  };

  recipes.forEach(recipe => {
    const collection = recipe.collection || '';
    if (counts.hasOwnProperty(collection)) {
      counts[collection]++;
    }
  });

  // Update button labels
  const labels = {
    '': 'All',
    'grandma': 'Grandma Baker',
    'mommom': 'MomMom Baker',
    'granny': 'Granny Hudson'
  };

  collectionFilters.querySelectorAll('.collection-btn').forEach(btn => {
    const collection = btn.dataset.collection;
    const label = labels[collection] || collection;
    const count = counts[collection] || 0;
    btn.textContent = `${label} (${count})`;
  });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Search form
  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = document.getElementById('search-input').value;
      currentFilter.search = query.toLowerCase();
      renderRecipeGrid();
    });
  }

  // Search input (live search)
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', debounce((e) => {
      currentFilter.search = e.target.value.toLowerCase();
      renderRecipeGrid();
    }, 300));
  }

  // Category filter
  const categorySelect = document.getElementById('category-filter');
  if (categorySelect) {
    categorySelect.addEventListener('change', (e) => {
      currentFilter.category = e.target.value;
      renderRecipeGrid();
    });
  }

  // Print button
  const printBtn = document.getElementById('print-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => window.print());
  }

  // Collection filter buttons
  const collectionFilters = document.getElementById('collection-filters');
  if (collectionFilters) {
    collectionFilters.querySelectorAll('.collection-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        // Update active state
        collectionFilters.querySelectorAll('.collection-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Update filter
        currentFilter.collection = btn.dataset.collection;
        renderRecipeGrid();
      });
    });
  }

  // Tags toggle (collapsible)
  const tagsToggle = document.getElementById('tags-toggle');
  const tagFilters = document.getElementById('tag-filters');
  if (tagsToggle && tagFilters) {
    tagsToggle.addEventListener('click', () => {
      const isExpanded = tagsToggle.getAttribute('aria-expanded') === 'true';
      tagsToggle.setAttribute('aria-expanded', !isExpanded);
      tagFilters.classList.toggle('collapsed', isExpanded);
    });
  }
}

/**
 * Handle client-side routing based on URL hash
 */
function handleRouting() {
  const path = window.location.pathname;
  const hash = window.location.hash;

  if (path.includes('recipe.html') && hash) {
    const recipeId = hash.slice(1);
    renderRecipeDetail(recipeId);
  } else if (path.includes('index.html') || path.endsWith('/')) {
    renderHomePage();
  }
}

/**
 * Render home page with recipe grid
 */
function renderHomePage() {
  renderCategoryFilter();
  renderTagFilters();
  renderRecipeGrid();
}

/**
 * Render category filter dropdown
 */
function renderCategoryFilter() {
  const select = document.getElementById('category-filter');
  if (!select) return;

  const sortedCategories = Array.from(categories).sort();
  let html = '<option value="">All Categories</option>';

  sortedCategories.forEach(cat => {
    html += `<option value="${escapeAttr(cat)}">${escapeHtml(capitalizeFirst(cat))}</option>`;
  });

  select.innerHTML = html;
}

/**
 * Render tag filter buttons
 */
function renderTagFilters() {
  const container = document.getElementById('tag-filters');
  if (!container) return;

  const sortedTags = Array.from(allTags).sort();
  let html = '';

  sortedTags.forEach(tag => {
    html += `<span class="filter-tag" data-tag="${escapeAttr(tag)}">${escapeHtml(tag)}</span>`;
  });

  container.innerHTML = html;

  // Add click handlers
  container.querySelectorAll('.filter-tag').forEach(el => {
    el.addEventListener('click', () => {
      const tag = el.dataset.tag;
      if (currentFilter.tag === tag) {
        currentFilter.tag = '';
        el.classList.remove('active');
      } else {
        container.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
        currentFilter.tag = tag;
        el.classList.add('active');
      }
      renderRecipeGrid();
    });
  });
}

/**
 * Render recipe grid with current filters
 */
function renderRecipeGrid() {
  const container = document.getElementById('recipe-grid');
  if (!container) return;

  // Filter recipes
  let filtered = recipes.filter(recipe => {
    // Exclude variants from main grid (show canonical only)
    if (recipe.variant_of && recipe.variant_of !== recipe.id) {
      return false;
    }

    // Search filter
    if (currentFilter.search) {
      const searchText = [
        recipe.title,
        recipe.description,
        recipe.attribution,
        ...recipe.tags || []
      ].join(' ').toLowerCase();

      if (!searchText.includes(currentFilter.search)) return false;
    }

    // Category filter
    if (currentFilter.category && recipe.category !== currentFilter.category) {
      return false;
    }

    // Tag filter
    if (currentFilter.tag && (!recipe.tags || !recipe.tags.includes(currentFilter.tag))) {
      return false;
    }

    // Collection filter
    if (currentFilter.collection && recipe.collection !== currentFilter.collection) {
      return false;
    }

    return true;
  });

  // Sort by title
  filtered.sort((a, b) => a.title.localeCompare(b.title));

  // Render
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center text-muted" style="grid-column: 1/-1; padding: 2rem;">
        <p>No recipes found matching your criteria.</p>
        <button class="btn btn-secondary" onclick="clearFilters()">Clear Filters</button>
      </div>
    `;
    return;
  }

  let html = '';
  filtered.forEach(recipe => {
    html += renderRecipeCard(recipe);
  });

  container.innerHTML = html;
}

/**
 * Render a single recipe card
 */
function renderRecipeCard(recipe) {
  const categoryIcon = getCategoryIcon(recipe.category);
  const timeInfo = recipe.total_time || recipe.cook_time || '';

  return `
    <article class="recipe-card category-${escapeAttr(recipe.category)}">
      <div class="recipe-card-image">
        ${categoryIcon}
      </div>
      <div class="recipe-card-content">
        <span class="category">${escapeHtml(recipe.category) || 'Uncategorized'}</span>
        <h3><a href="recipe.html#${escapeAttr(recipe.id)}">${escapeHtml(recipe.title)}</a></h3>
        <p class="description">${escapeHtml(recipe.description)}</p>
        <div class="meta">
          ${recipe.servings_yield ? `<span>${escapeHtml(recipe.servings_yield)}</span>` : ''}
          ${timeInfo ? `<span>${escapeHtml(timeInfo)}</span>` : ''}
        </div>
      </div>
    </article>
  `;
}

/**
 * Render full recipe detail page
 */
function renderRecipeDetail(recipeId) {
  const recipe = recipes.find(r => r.id === recipeId);
  const container = document.getElementById('recipe-content');

  if (!recipe || !container) {
    if (container) {
      container.innerHTML = `
        <div class="text-center">
          <h2>Recipe Not Found</h2>
          <p>Sorry, we couldn't find that recipe.</p>
          <a href="index.html" class="btn btn-primary">Back to Recipes</a>
        </div>
      `;
    }
    return;
  }

  // Find variants of this recipe
  const variants = findVariants(recipe);

  // Update page title
  document.title = `${recipe.title} - Grandma's Recipe Archive`;

  let html = `
    <article class="recipe-detail">
      <header class="recipe-header">
        <h1>${escapeHtml(recipe.title)}</h1>
        ${recipe.attribution ? `<p class="recipe-attribution">From: ${escapeHtml(recipe.attribution)}</p>` : ''}
        ${recipe.source_note ? `<p class="recipe-source">${escapeHtml(recipe.source_note)}</p>` : ''}
        ${recipe.description ? `<p>${escapeHtml(recipe.description)}</p>` : ''}

        <div class="header-controls">
          <div class="confidence-indicator confidence-${escapeAttr(recipe.confidence?.overall || 'high')}">
            Confidence: ${escapeHtml(capitalizeFirst(recipe.confidence?.overall || 'high'))}
          </div>

          ${variants.length > 0 ? renderVariantsDropdown(recipe, variants) : ''}
        </div>

        <div class="action-buttons" style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button id="print-btn" class="btn btn-secondary btn-print">Print Recipe</button>
          ${recipe.conversions?.has_conversions ? `
            <button id="metric-toggle" class="btn btn-secondary">
              ${showMetric ? 'Show US Units' : 'Show Metric'}
            </button>
          ` : ''}
        </div>
      </header>

      ${renderQuickFacts(recipe)}

      <section class="ingredients-section">
        <h2>Ingredients ${showMetric && recipe.conversions?.has_conversions ? '<span class="unit-badge">Metric (approx.)</span>' : ''}</h2>
        ${renderIngredientsList(recipe)}
      </section>

      <section class="instructions-section">
        <h2>Instructions</h2>
        <ol class="instructions-list">
          ${recipe.instructions.map(inst => {
            const isInferred = inst.text.includes('[INFERRED]');
            const text = inst.text.replace('[INFERRED] ', '');
            return `<li class="${isInferred ? 'inferred' : ''}">${escapeHtml(text)}</li>`;
          }).join('')}
        </ol>
      </section>

      ${recipe.oven_directions ? renderOvenDirections(recipe.oven_directions) : ''}
      ${recipe.frosting ? renderFrosting(recipe.frosting) : ''}
      ${recipe.nutrition ? renderNutrition(recipe.nutrition, recipe.servings_yield) : ''}
      ${recipe.notes && recipe.notes.length > 0 ? renderNotes(recipe.notes) : ''}
      ${recipe.conversions?.conversion_assumptions?.length > 0 && showMetric ? renderConversionNotes(recipe.conversions) : ''}
      ${renderTags(recipe.tags)}
      ${renderConfidenceFlags(recipe.confidence?.flags)}
      ${renderOriginalScan(recipe.image_refs, recipe.collection)}
    </article>
  `;

  container.innerHTML = html;

  // Re-attach event listeners
  const printBtn = document.getElementById('print-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => window.print());
  }

  const metricToggle = document.getElementById('metric-toggle');
  if (metricToggle) {
    metricToggle.addEventListener('click', () => {
      showMetric = !showMetric;
      renderRecipeDetail(recipeId);
    });
  }

  // Variant dropdown handler
  const variantSelect = document.getElementById('variant-select');
  if (variantSelect) {
    variantSelect.addEventListener('change', (e) => {
      if (e.target.value) {
        window.location.hash = e.target.value;
        renderRecipeDetail(e.target.value);
      }
    });
  }
}

/**
 * Find all variants of a recipe (or recipes this is a variant of)
 */
function findVariants(recipe) {
  const variants = [];
  const canonicalId = recipe.canonical_id || recipe.id;

  recipes.forEach(r => {
    if (r.id === recipe.id) return; // Skip self

    // Check if this recipe is a variant of the current one
    if (r.variant_of === recipe.id || r.variant_of === canonicalId) {
      variants.push(r);
    }
    // Check if current recipe is a variant and find siblings
    if (recipe.variant_of && (r.id === recipe.variant_of || r.variant_of === recipe.variant_of)) {
      if (r.id !== recipe.id) variants.push(r);
    }
    // Check canonical grouping
    if (r.canonical_id === canonicalId && r.id !== recipe.id) {
      variants.push(r);
    }
  });

  return variants;
}

/**
 * Render variants dropdown
 */
function renderVariantsDropdown(currentRecipe, variants) {
  return `
    <div class="variants-dropdown">
      <label for="variant-select">Variants:</label>
      <select id="variant-select" class="variant-select">
        <option value="${escapeAttr(currentRecipe.id)}" selected>${escapeHtml(currentRecipe.source_note || 'Current version')}</option>
        ${variants.map(v => `
          <option value="${escapeAttr(v.id)}">${escapeHtml(v.source_note || v.title)}${v.variant_notes ? ` - ${escapeHtml(v.variant_notes.substring(0, 50))}...` : ''}</option>
        `).join('')}
      </select>
    </div>
  `;
}

/**
 * Render ingredients list (with metric toggle support)
 */
function renderIngredientsList(recipe) {
  const ingredients = showMetric && recipe.conversions?.ingredients_metric?.length > 0
    ? recipe.conversions.ingredients_metric
    : recipe.ingredients;

  return `
    <ul class="ingredients-list">
      ${ingredients.map(ing => `
        <li>
          <span class="ingredient-quantity">${escapeHtml(ing.quantity)} ${escapeHtml(ing.unit)}</span>
          <span class="ingredient-item">
            ${escapeHtml(ing.item)}
            ${ing.prep_note ? `<span class="ingredient-prep">, ${escapeHtml(ing.prep_note)}</span>` : ''}
          </span>
        </li>
      `).join('')}
    </ul>
  `;
}

/**
 * Render nutrition information
 */
function renderNutrition(nutrition, servings) {
  if (!nutrition || nutrition.status === 'insufficient_data') {
    if (nutrition?.missing_inputs?.length > 0) {
      return `
        <section class="nutrition-section nutrition-incomplete">
          <h3>Nutrition Information</h3>
          <p class="text-muted">Nutrition data incomplete. Missing: ${escapeHtml(nutrition.missing_inputs.join(', '))}</p>
        </section>
      `;
    }
    return '';
  }

  const n = nutrition.per_serving;
  if (!n) return '';

  return `
    <section class="nutrition-section">
      <h3>Nutrition Information ${servings ? `<span class="text-muted">(per serving)</span>` : ''}</h3>
      <div class="nutrition-grid">
        ${n.calories !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.calories)}</span><span class="nutrition-label">Calories</span></div>` : ''}
        ${n.fat_g !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.fat_g)}g</span><span class="nutrition-label">Fat</span></div>` : ''}
        ${n.carbs_g !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.carbs_g)}g</span><span class="nutrition-label">Carbs</span></div>` : ''}
        ${n.protein_g !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.protein_g)}g</span><span class="nutrition-label">Protein</span></div>` : ''}
        ${n.sodium_mg !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.sodium_mg)}mg</span><span class="nutrition-label">Sodium</span></div>` : ''}
        ${n.fiber_g !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.fiber_g)}g</span><span class="nutrition-label">Fiber</span></div>` : ''}
        ${n.sugar_g !== null ? `<div class="nutrition-item"><span class="nutrition-value">${escapeHtml(n.sugar_g)}g</span><span class="nutrition-label">Sugar</span></div>` : ''}
      </div>
      ${nutrition.assumptions?.length > 0 ? `
        <p class="nutrition-assumptions text-muted">
          <small>Assumptions: ${escapeHtml(nutrition.assumptions.join('; '))}</small>
        </p>
      ` : ''}
    </section>
  `;
}

/**
 * Render conversion notes
 */
function renderConversionNotes(conversions) {
  if (!conversions?.conversion_assumptions?.length) return '';

  return `
    <section class="notes-section conversion-notes" style="border-left-color: #6c757d;">
      <h3>Conversion Notes</h3>
      <p class="text-muted"><small>Metric conversions are approximate. Assumptions used:</small></p>
      <ul>
        ${conversions.conversion_assumptions.map(a => `<li><small>${escapeHtml(a)}</small></li>`).join('')}
      </ul>
    </section>
  `;
}

/**
 * Render quick facts section
 */
function renderQuickFacts(recipe) {
  const facts = [];

  if (recipe.servings_yield) facts.push({ label: 'Yield', value: recipe.servings_yield });
  if (recipe.prep_time) facts.push({ label: 'Prep', value: recipe.prep_time });
  if (recipe.cook_time) facts.push({ label: 'Cook', value: recipe.cook_time });
  if (recipe.total_time) facts.push({ label: 'Total', value: recipe.total_time });
  if (recipe.temperature) facts.push({ label: 'Temp', value: recipe.temperature });

  if (facts.length === 0) return '';

  return `
    <div class="recipe-quick-facts">
      ${facts.map(f => `
        <div class="quick-fact">
          <span class="quick-fact-label">${escapeHtml(f.label)}</span>
          <span class="quick-fact-value">${escapeHtml(f.value)}</span>
        </div>
      `).join('')}
    </div>
  `;
}

/**
 * Render oven directions (alternative method)
 */
function renderOvenDirections(directions) {
  return `
    <section class="sub-recipe">
      <h3>Oven Directions (Alternative)</h3>
      <ol class="instructions-list">
        ${directions.map(d => `<li>${escapeHtml(d.text)}</li>`).join('')}
      </ol>
    </section>
  `;
}

/**
 * Render frosting/sub-recipe section
 */
function renderFrosting(frosting) {
  return `
    <section class="sub-recipe">
      <h3>${escapeHtml(frosting.name)}</h3>
      <h4>Ingredients:</h4>
      <ul class="ingredients-list">
        ${frosting.ingredients.map(ing => `
          <li>
            <span class="ingredient-quantity">${escapeHtml(ing.quantity)} ${escapeHtml(ing.unit)}</span>
            <span class="ingredient-item">${escapeHtml(ing.item)}</span>
          </li>
        `).join('')}
      </ul>
      <h4>Instructions:</h4>
      <p>${escapeHtml(frosting.instructions)}</p>
    </section>
  `;
}

/**
 * Render notes section
 */
function renderNotes(notes) {
  return `
    <section class="notes-section">
      <h3>Notes</h3>
      <ul>
        ${notes.map(note => `<li>${escapeHtml(note)}</li>`).join('')}
      </ul>
    </section>
  `;
}

/**
 * Render tags
 */
function renderTags(tags) {
  if (!tags || tags.length === 0) return '';

  return `
    <div class="recipe-tags">
      ${tags.map(tag => `<span class="recipe-tag">${escapeHtml(tag)}</span>`).join('')}
    </div>
  `;
}

/**
 * Render confidence flags if any
 */
function renderConfidenceFlags(flags) {
  if (!flags || flags.length === 0) return '';

  return `
    <section class="notes-section" style="border-left-color: #f0ad4e;">
      <h3>Transcription Notes</h3>
      <ul>
        ${flags.map(flag => `
          <li>
            <strong>${escapeHtml(flag.field)}:</strong> ${escapeHtml(flag.issue)}
            ${flag.candidates && flag.candidates.length > 0 ?
              `<br><em>Possible values: ${escapeHtml(flag.candidates.join(', '))}</em>` : ''}
          </li>
        `).join('')}
      </ul>
    </section>
  `;
}

/**
 * Get the folder path for a collection's images
 */
function getCollectionImagePath(collection) {
  const collectionPaths = {
    'grandma': 'grandma/',
    'mommom': 'mom/',
    'granny': 'granny/',
    'reference': 'all/'
  };
  return collectionPaths[collection] || 'grandma/';
}

/**
 * Render original scan thumbnail
 */
function renderOriginalScan(imageRefs, collection) {
  if (!imageRefs || imageRefs.length === 0) return '';

  const basePath = getCollectionImagePath(collection);

  return `
    <section class="original-scan">
      <h3>Original Scan</h3>
      ${imageRefs.map(ref => {
        const safePath = sanitizeUrl(basePath + ref);
        return `
        <a href="${escapeAttr(safePath)}" target="_blank">
          <img src="${escapeAttr(safePath)}" alt="Original recipe scan" class="scan-thumbnail"
               style="max-width: 200px; max-height: 150px; object-fit: cover;">
        </a>
      `;}).join('')}
    </section>
  `;
}

/**
 * Get category icon (emoji)
 */
function getCategoryIcon(category) {
  const icons = {
    appetizers: '🥗',
    beverages: '🍹',
    breads: '🍞',
    breakfast: '🍳',
    desserts: '🍪',
    mains: '🍽️',
    salads: '🥬',
    sides: '🥕',
    soups: '🍲',
    snacks: '🍿'
  };
  return icons[category] || '📖';
}

/**
 * Clear all filters
 */
function clearFilters() {
  currentFilter = { search: '', category: '', tag: '', collection: '' };

  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.value = '';

  const categorySelect = document.getElementById('category-filter');
  if (categorySelect) categorySelect.value = '';

  document.querySelectorAll('.filter-tag').forEach(el => el.classList.remove('active'));

  // Reset collection buttons
  const collectionFilters = document.getElementById('collection-filters');
  if (collectionFilters) {
    collectionFilters.querySelectorAll('.collection-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.collection === '');
    });
  }

  renderRecipeGrid();
}

// Make clearFilters available globally
window.clearFilters = clearFilters;

/**
 * Utility: Capitalize first letter
 */
function capitalizeFirst(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Utility: Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Show error message
 */
function showError(message) {
  const container = document.getElementById('recipe-grid') || document.getElementById('recipe-content');
  if (container) {
    container.innerHTML = `
      <div class="text-center" style="padding: 2rem; color: #721c24; background: #f8d7da; border-radius: 8px;">
        <p>${escapeHtml(message)}</p>
      </div>
    `;
  }
}
