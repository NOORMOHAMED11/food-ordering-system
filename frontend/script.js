let cart = [];       // [{menu_item_id, name, price, quantity}]
let menuCache = [];
let activeCategory = null;

// ---------------- Navigation ----------------
document.querySelectorAll('nav a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    link.classList.add('active');
    const view = link.dataset.view;
    document.getElementById(view).classList.add('active');
    if (view === 'orders') loadOrders();
  });
});

// ---------------- Menu ----------------
async function fetchMenu() {
  const res = await fetch('/api/menu');
  menuCache = await res.json();
  renderFilters();
  renderMenu();
}

function renderFilters() {
  const categories = [...new Set(menuCache.map(i => i.category))];
  const container = document.getElementById('filters');
  container.innerHTML = '';
  const allBtn = document.createElement('button');
  allBtn.textContent = 'All';
  allBtn.className = activeCategory === null ? 'active' : '';
  allBtn.onclick = () => { activeCategory = null; renderFilters(); renderMenu(); };
  container.appendChild(allBtn);

  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.textContent = cat;
    btn.className = activeCategory === cat ? 'active' : '';
    btn.onclick = () => { activeCategory = cat; renderFilters(); renderMenu(); };
    container.appendChild(btn);
  });
}

function renderMenu() {
  const container = document.getElementById('menu-container');
  container.innerHTML = '';
  const items = activeCategory ? menuCache.filter(i => i.category === activeCategory) : menuCache;

  items.forEach(item => {
    const div = document.createElement('div');
    div.className = 'menu-item';
    div.innerHTML = `
      <div class="emoji">${item.image_emoji}</div>
      <h3>${item.name}</h3>
      <p>${item.description || ''}</p>
      <span class="price">₹${item.price.toFixed(2)}</span>
      <button class="add-btn">Add to Cart</button>
    `;
    div.querySelector('.add-btn').onclick = () => addToCart(item);
    container.appendChild(div);
  });
}

// ---------------- Cart ----------------
function addToCart(item) {
  const existing = cart.find(c => c.menu_item_id === item.id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ menu_item_id: item.id, name: item.name, price: item.price, quantity: 1 });
  }
  updateCartUI();
}

function removeFromCart(menuItemId) {
  cart = cart.filter(c => c.menu_item_id !== menuItemId);
  updateCartUI();
}

function changeQty(menuItemId, delta) {
  const item = cart.find(c => c.menu_item_id === menuItemId);
  if (!item) return;
  item.quantity += delta;
  if (item.quantity <= 0) {
    removeFromCart(menuItemId);
  } else {
    updateCartUI();
  }
}

function updateCartUI() {
  const totalCount = cart.reduce((s, i) => s + i.quantity, 0);
  document.getElementById('cart-count').textContent = totalCount;

  const container = document.getElementById('cart-items');
  if (cart.length === 0) {
    container.innerHTML = '<p class="empty-msg">Your cart is empty. Add something tasty!</p>';
    document.getElementById('total').textContent = '0.00';
    return;
  }

  container.innerHTML = '';
  let total = 0;
  cart.forEach(item => {
    total += item.price * item.quantity;
    const row = document.createElement('div');
    row.className = 'cart-row';
    row.innerHTML = `
      <span>${item.name}</span>
      <span>
        <button onclick="changeQty(${item.menu_item_id}, -1)">−</button>
        ${item.quantity}
        <button onclick="changeQty(${item.menu_item_id}, 1)">+</button>
        &nbsp;₹${(item.price * item.quantity).toFixed(2)}
        <button onclick="removeFromCart(${item.menu_item_id})">Remove</button>
      </span>
    `;
    container.appendChild(row);
  });
  document.getElementById('total').textContent = total.toFixed(2);
}

// ---------------- Checkout ----------------
async function checkout() {
  if (cart.length === 0) {
    alert('Your cart is empty!');
    return;
  }
  const customer_name = document.getElementById('customer_name').value.trim();
  if (!customer_name) {
    alert('Please enter your name.');
    return;
  }
  const customer_phone = document.getElementById('customer_phone').value.trim();
  const address = document.getElementById('address').value.trim();

  const orderData = {
    customer_name,
    customer_phone,
    address,
    items: cart.map(i => ({ menu_item_id: i.menu_item_id, quantity: i.quantity }))
  };

  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    });
    if (!res.ok) throw new Error('Order failed');
    const result = await res.json();
    alert(`Order placed! Order ID: #${result.id}\nTotal: ₹${result.total_amount.toFixed(2)}`);
    cart = [];
    updateCartUI();
    document.getElementById('customer_name').value = '';
    document.getElementById('customer_phone').value = '';
    document.getElementById('address').value = '';
    document.querySelector('a[data-view="orders"]').click();
  } catch (err) {
    console.error(err);
    alert('Something went wrong placing your order. Please try again.');
  }
}

// ---------------- Orders ----------------
async function loadOrders() {
  const container = document.getElementById('orders-container');
  container.innerHTML = 'Loading...';
  const res = await fetch('/api/orders');
  const orders = await res.json();

  if (orders.length === 0) {
    container.innerHTML = '<p class="empty-msg">No orders yet.</p>';
    return;
  }

  container.innerHTML = '';
  orders.forEach(order => {
    const card = document.createElement('div');
    card.className = 'order-card';
    const itemsList = order.items.map(i => `${i.item_name} x${i.quantity}`).join(', ');
    card.innerHTML = `
      <div class="order-head">
        <strong>Order #${order.id}</strong>
        <span class="status-badge ${order.status}">${order.status.replace('_', ' ')}</span>
      </div>
      <p>${itemsList}</p>
      <p><strong>Total: ₹${order.total_amount.toFixed(2)}</strong></p>
      <small>${new Date(order.created_at).toLocaleString()}</small>
    `;
    container.appendChild(card);
  });
}

// ---------------- Init ----------------
document.addEventListener('DOMContentLoaded', () => {
  fetchMenu();
  updateCartUI();
});
