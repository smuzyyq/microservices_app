const API = {
  auth: "/api/auth/auth",
  products: "/api/products/products",
  orders: "/api/orders/orders",
  users: "/api/users/users",
  chat: "/api/chat/chat",
  health: {
    auth: "/api/auth/health",
    product: "/api/products/health",
    order: "/api/orders/health",
    user: "/api/users/health",
    chat: "/api/chat/health",
  },
};

const ROLE_VIEWS = {
  customer: ["overview", "restaurants", "menu", "orders", "chat", "profile"],
  courier: ["overview", "delivery", "chat", "profile"],
  admin: ["overview", "restaurants", "menu", "orders", "delivery", "chat", "profile"],
};

const NEXT_STATUS = {
  pending: "confirmed",
  confirmed: "preparing",
  preparing: "delivering",
  delivering: "delivered",
};

const state = {
  token: localStorage.getItem("foodrush_token") || "",
  currentUser: JSON.parse(localStorage.getItem("foodrush_user") || "null"),
  restaurants: [],
  filteredRestaurants: [],
  selectedRestaurant: null,
  selectedMenu: [],
  cart: [],
  orders: [],
  deliveryOrders: [],
  profile: null,
  addresses: [],
  rooms: [],
  activeChatOrderId: null,
  activeRoom: null,
  chatMessages: [],
  restaurantQuery: "",
  deliveryRestaurantId: "",
  selectedCheckoutAddressId: "",
};

const elements = {
  authView: document.getElementById("auth-view"),
  appView: document.getElementById("app-view"),
  authMessage: document.getElementById("auth-message"),
  orderMessage: document.getElementById("order-message"),
  chatMessage: document.getElementById("chat-message"),
  loginForm: document.getElementById("login-form"),
  registerForm: document.getElementById("register-form"),
  logoutButton: document.getElementById("logout-button"),
  showLogin: document.getElementById("show-login"),
  showRegister: document.getElementById("show-register"),
  workspaceTitle: document.getElementById("workspace-title"),
  workspaceSubtitle: document.getElementById("workspace-subtitle"),
  userRoleBadge: document.getElementById("user-role-badge"),
  userName: document.getElementById("user-name"),
  userEmail: document.getElementById("user-email"),
  summaryRestaurants: document.getElementById("summary-restaurants"),
  summaryOrders: document.getElementById("summary-orders"),
  summaryChats: document.getElementById("summary-chats"),
  overviewHighlights: document.getElementById("overview-highlights"),
  overviewFeed: document.getElementById("overview-feed"),
  restaurantSearch: document.getElementById("restaurant-search"),
  restaurantsGrid: document.getElementById("restaurants-grid"),
  menuGrid: document.getElementById("menu-grid"),
  menuTitle: document.getElementById("menu-title"),
  menuSubtitle: document.getElementById("menu-subtitle"),
  cartItems: document.getElementById("cart-items"),
  cartCount: document.getElementById("cart-count"),
  cartTotal: document.getElementById("cart-total"),
  cartSidebar: document.getElementById("cart-sidebar"),
  checkoutForm: document.getElementById("checkout-form"),
  savedAddressSelect: document.getElementById("saved-address-select"),
  checkoutAddressHint: document.getElementById("checkout-address-hint"),
  ordersList: document.getElementById("orders-list"),
  deliveryRestaurantSelect: document.getElementById("delivery-restaurant-select"),
  deliveryOrdersList: document.getElementById("delivery-orders-list"),
  profileForm: document.getElementById("profile-form"),
  addressForm: document.getElementById("address-form"),
  addressesList: document.getElementById("addresses-list"),
  chatOrderList: document.getElementById("chat-order-list"),
  chatMessages: document.getElementById("chat-messages"),
  chatForm: document.getElementById("chat-form"),
  chatInput: document.getElementById("chat-input"),
  chatRoomMeta: document.getElementById("chat-room-meta"),
  refreshRestaurants: document.getElementById("refresh-restaurants"),
  refreshOrders: document.getElementById("refresh-orders"),
  refreshDeliveries: document.getElementById("refresh-deliveries"),
  healthStatuses: document.getElementById("health-statuses"),
  navButtons: [...document.querySelectorAll(".nav-button")],
  roleControlled: [...document.querySelectorAll("[data-roles]")],
  views: {
    overview: document.getElementById("overview-view"),
    restaurants: document.getElementById("restaurants-view"),
    menu: document.getElementById("menu-view"),
    orders: document.getElementById("orders-view"),
    delivery: document.getElementById("delivery-view"),
    chat: document.getElementById("chat-view"),
    profile: document.getElementById("profile-view"),
  },
};

function getRole() {
  return state.currentUser?.role || "customer";
}

function isRole(...roles) {
  return roles.includes(getRole());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function normalizeErrorDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          const location = Array.isArray(item.loc) ? item.loc.join(" -> ") : null;
          const message = item.msg || JSON.stringify(item);
          return location ? `${location}: ${message}` : message;
        }
        return String(item);
      })
      .join("; ");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }

  return "Request failed.";
}

function formatMoney(value) {
  return `$${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "Not available";
}

function capitalize(value) {
  return String(value || "").charAt(0).toUpperCase() + String(value || "").slice(1);
}

function sortOrdersByCreatedAt(orders) {
  return [...orders].sort((left, right) => new Date(right.created_at) - new Date(left.created_at));
}

function setMessage(target, message, isError = false) {
  target.textContent = message;
  target.classList.toggle("error", isError);
}

function saveSession(token, user) {
  state.token = token;
  state.currentUser = user;
  localStorage.setItem("foodrush_token", token);
  localStorage.setItem("foodrush_user", JSON.stringify(user));
}

function clearSession() {
  state.token = "";
  state.currentUser = null;
  state.restaurants = [];
  state.filteredRestaurants = [];
  state.selectedRestaurant = null;
  state.selectedMenu = [];
  state.cart = [];
  state.orders = [];
  state.deliveryOrders = [];
  state.profile = null;
  state.addresses = [];
  state.rooms = [];
  state.activeChatOrderId = null;
  state.activeRoom = null;
  state.chatMessages = [];
  state.restaurantQuery = "";
  state.deliveryRestaurantId = "";
  state.selectedCheckoutAddressId = "";
  localStorage.removeItem("foodrush_token");
  localStorage.removeItem("foodrush_user");
}

async function request(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const data = await response.json();
      detail = normalizeErrorDetail(data.detail ?? data);
    } catch {
      detail = response.statusText || detail;
    }

    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function updateAuthUI() {
  const authenticated = Boolean(state.token);
  elements.authView.classList.toggle("hidden", authenticated);
  elements.appView.classList.toggle("hidden", !authenticated);
  elements.logoutButton.classList.toggle("hidden", !authenticated);
}

function switchAuthMode(mode) {
  const isLogin = mode === "login";
  elements.loginForm.classList.toggle("hidden", !isLogin);
  elements.registerForm.classList.toggle("hidden", isLogin);
  elements.showLogin.classList.toggle("active", isLogin);
  elements.showRegister.classList.toggle("active", !isLogin);
  setMessage(elements.authMessage, "");
}

function getAvailableViews() {
  return ROLE_VIEWS[getRole()] || ROLE_VIEWS.customer;
}

function getDefaultView() {
  const views = getAvailableViews();
  return views.includes("overview") ? "overview" : views[0];
}

function applyRoleVisibility() {
  const role = getRole();

  elements.roleControlled.forEach((element) => {
    const roles = String(element.dataset.roles || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    if (!roles.length) {
      return;
    }
    element.classList.toggle("hidden", !roles.includes(role));
  });
}

function switchView(viewName) {
  const available = getAvailableViews();
  const nextView = available.includes(viewName) ? viewName : getDefaultView();

  elements.navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === nextView);
  });

  Object.entries(elements.views).forEach(([name, view]) => {
    view.classList.toggle("hidden", name !== nextView);
  });
}

function getRestaurantNameById(restaurantId) {
  return state.restaurants.find((restaurant) => restaurant.id === restaurantId)?.name || "Restaurant";
}

function getRestaurantCity(address) {
  const pieces = String(address || "")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
  return pieces[pieces.length - 1] || "Kazakhstan";
}

function getOrderSource() {
  return isRole("courier") ? state.deliveryOrders : state.orders;
}

function getOrderById(orderId) {
  return [...state.orders, ...state.deliveryOrders].find((order) => order.id === orderId) || null;
}

function getRoomForOrder(orderId) {
  return state.rooms.find((room) => room.order_id === orderId) || null;
}

function syncRoomCache(room) {
  if (!room) {
    return;
  }

  const existingIndex = state.rooms.findIndex((item) => item.id === room.id);
  if (existingIndex >= 0) {
    state.rooms[existingIndex] = room;
  } else {
    state.rooms.push(room);
  }
}

function updateWorkspaceMeta() {
  const user = state.currentUser || {};
  const role = getRole();
  const roleText = role === "courier" ? "Courier Desk" : role === "admin" ? "Admin Console" : "Customer Lounge";

  elements.workspaceTitle.textContent = `${roleText} for ${user.full_name || "FoodRush"}`;
  elements.workspaceSubtitle.textContent =
    role === "courier"
      ? "Review restaurant queues, update delivery statuses, and jump into active delivery chats."
      : role === "admin"
        ? "You can inspect storefront data, own orders, courier dispatch boards, and operational chat threads."
        : "Browse restaurants, place orders with clearer address handling, and chat around deliveries.";

  elements.userRoleBadge.textContent = role;
  elements.userName.textContent = user.full_name || "Guest";
  elements.userEmail.textContent = user.email || "";
  elements.summaryRestaurants.textContent = String(state.restaurants.length);
  elements.summaryOrders.textContent = String(getOrderSource().length);
  elements.summaryChats.textContent = String(state.rooms.length);
}

function renderHealthStatuses(results = {}) {
  const services = [
    { key: "auth", label: "Auth" },
    { key: "product", label: "Product" },
    { key: "order", label: "Order" },
    { key: "user", label: "User" },
    { key: "chat", label: "Chat" },
  ];

  elements.healthStatuses.innerHTML = services
    .map(({ key, label }) => {
      const stateText = results[key] || "down";
      const statusClass = stateText === "ok" ? "ok" : stateText === "degraded" ? "degraded" : "";
      return `
        <span class="health-chip">
          <span class="health-dot ${statusClass}"></span>
          ${escapeHtml(label)}
        </span>
      `;
    })
    .join("");
}

async function pollHealth() {
  const results = {};

  await Promise.all(
    Object.entries(API.health).map(async ([key, url]) => {
      try {
        const response = await fetch(url);
        const data = await response.json();
        results[key] = data.status || "down";
      } catch {
        results[key] = "down";
      }
    }),
  );

  renderHealthStatuses(results);
}

function renderOverview() {
  const role = getRole();
  const activeOrders = getOrderSource().filter((order) => !["delivered", "cancelled"].includes(order.status));
  const defaultAddress = state.addresses.find((address) => address.is_default) || state.addresses[0] || null;

  const highlights =
    role === "courier"
      ? [
          { title: "Restaurant queue", value: state.deliveryOrders.length, text: "Orders currently visible in your selected dispatch board." },
          { title: "Needs action", value: activeOrders.length, text: "Deliveries that still need confirmation, prep, or drop-off." },
          { title: "Claimed chats", value: state.rooms.length, text: "Delivery conversations currently assigned to your account." },
        ]
      : [
          { title: "Open restaurants", value: state.restaurants.filter((item) => item.is_open).length, text: "Kazakhstan-inspired restaurant lineup available right now." },
          { title: "Active orders", value: activeOrders.length, text: "Orders that are still moving through prep or delivery." },
          { title: "Saved addresses", value: state.addresses.length, text: "Address book entries ready for one-tap checkout." },
        ];

  elements.overviewHighlights.innerHTML = highlights
    .map(
      (item) => `
        <article class="highlight-card">
          <p class="section-label">${escapeHtml(item.title)}</p>
          <strong>${escapeHtml(item.value)}</strong>
          <p>${escapeHtml(item.text)}</p>
        </article>
      `,
    )
    .join("");

  const feedItems = [];

  if (role === "courier") {
    if (state.deliveryRestaurantId) {
      feedItems.push(`
        <article class="overview-panel">
          <p class="section-label">Selected board</p>
          <h4>${escapeHtml(getRestaurantNameById(state.deliveryRestaurantId))}</h4>
          <p>Use the delivery board to move orders through each status and jump into order chats when customers need help.</p>
        </article>
      `);
    }
  } else {
    feedItems.push(`
      <article class="overview-panel">
        <p class="section-label">Default address</p>
        <h4>${escapeHtml(defaultAddress?.label || "No default address yet")}</h4>
        <p>${escapeHtml(defaultAddress?.full_address || "Add a saved address to speed up checkout and reduce delivery confusion.")}</p>
      </article>
    `);
  }

  const featuredRestaurants = state.restaurants.slice(0, 3);
  if (featuredRestaurants.length) {
    feedItems.push(`
      <article class="overview-panel">
        <p class="section-label">Featured places</p>
        <h4>${featuredRestaurants.map((restaurant) => escapeHtml(restaurant.name)).join(" • ")}</h4>
        <p>Fresh mix of local comfort food, street-food favorites, and city staples across Almaty, Astana, and beyond.</p>
      </article>
    `);
  }

  elements.overviewFeed.innerHTML = feedItems.join("");
}

function renderRestaurants() {
  const query = state.restaurantQuery.trim().toLowerCase();
  state.filteredRestaurants = state.restaurants.filter((restaurant) => {
    const haystack = [restaurant.name, restaurant.cuisine_type, restaurant.description, restaurant.address]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  });

  if (!state.filteredRestaurants.length) {
    elements.restaurantsGrid.innerHTML = '<p class="empty-state">No restaurants matched your search.</p>';
    return;
  }

  elements.restaurantsGrid.innerHTML = state.filteredRestaurants
    .map(
      (restaurant) => `
        <article class="card">
          <div class="card-hero">
            <div class="card-topline">
              <span class="meta-pill">${escapeHtml(restaurant.cuisine_type)}</span>
              <span class="meta-pill">${restaurant.is_open ? "Open now" : "Closed"}</span>
            </div>
            <div>
              <h4>${escapeHtml(restaurant.name)}</h4>
              <p>${escapeHtml(getRestaurantCity(restaurant.address))}</p>
            </div>
          </div>
          <p>${escapeHtml(restaurant.description)}</p>
          <p>${escapeHtml(restaurant.address)}</p>
          <div class="card-footer">
            <strong>${escapeHtml(`⭐ ${Number(restaurant.rating).toFixed(1)}`)}</strong>
            <button class="primary-button" type="button" data-action="open-menu" data-id="${restaurant.id}">
              Open menu
            </button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderMenu() {
  if (!state.selectedRestaurant) {
    elements.menuGrid.innerHTML = '<p class="empty-state">Choose a restaurant to view dishes.</p>';
    return;
  }

  elements.menuTitle.textContent = state.selectedRestaurant.name;
  elements.menuSubtitle.textContent = `${state.selectedRestaurant.cuisine_type} • ${state.selectedRestaurant.address}`;

  elements.menuGrid.innerHTML = state.selectedMenu
    .map(
      (dish) => `
        <article class="card">
          <div class="card-topline">
            <span class="meta-pill">${escapeHtml(dish.category)}</span>
            <span class="meta-pill">${dish.is_available ? "Available" : "Unavailable"}</span>
          </div>
          <h4>${escapeHtml(dish.name)}</h4>
          <p>${escapeHtml(dish.description)}</p>
          <div class="card-footer">
            <span class="dish-price">${formatMoney(dish.price)}</span>
            <button
              class="secondary-button"
              type="button"
              data-action="add-to-cart"
              data-id="${dish.id}"
              ${dish.is_available ? "" : "disabled"}
            >
              Add to cart
            </button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderCart() {
  const canUseCart = isRole("customer", "admin");
  elements.cartSidebar.classList.toggle("hidden", !canUseCart);

  if (!canUseCart) {
    return;
  }

  elements.cartCount.textContent = String(
    state.cart.reduce((total, item) => total + Number(item.quantity), 0),
  );

  if (!state.cart.length) {
    elements.cartItems.innerHTML = '<p class="empty-state">Your cart is empty.</p>';
    elements.cartTotal.textContent = "$0.00";
    return;
  }

  let total = 0;
  elements.cartItems.innerHTML = state.cart
    .map((item) => {
      total += Number(item.quantity) * Number(item.price);
      return `
        <article class="cart-item">
          <div class="cart-total-row">
            <strong>${escapeHtml(item.name)}</strong>
            <button class="ghost-button" type="button" data-action="remove-from-cart" data-id="${item.id}">
              Remove
            </button>
          </div>
          <p>${escapeHtml(item.restaurantName)}</p>
          <p>${escapeHtml(`${item.quantity} × ${formatMoney(item.price)}`)}</p>
        </article>
      `;
    })
    .join("");

  elements.cartTotal.textContent = formatMoney(total);
}

function renderOrders() {
  if (!state.orders.length) {
    elements.ordersList.innerHTML = '<p class="empty-state">No orders yet. Browse restaurants and place your first one.</p>';
    return;
  }

  elements.ordersList.innerHTML = state.orders
    .map(
      (order) => `
        <article class="order-card">
          <div class="order-topline">
            <div>
              <p class="section-label">${escapeHtml(getRestaurantNameById(order.restaurant_id))}</p>
              <h4>Order #${escapeHtml(String(order.id).slice(0, 8))}</h4>
            </div>
            <span class="status-badge status-${order.status}">${escapeHtml(order.status)}</span>
          </div>
          <p><strong>Delivery address:</strong> ${escapeHtml(order.delivery_address)}</p>
          <p><strong>Created:</strong> ${escapeHtml(formatDate(order.created_at))}</p>
          <div class="item-list">
            ${order.items
              .map(
                (item) =>
                  `<span class="item-chip">${escapeHtml(`${item.quantity}× ${item.dish_name}`)}</span>`,
              )
              .join("")}
          </div>
          <div class="order-actions">
            <strong>${formatMoney(order.total_price)}</strong>
            <div class="section-actions">
              <button class="ghost-button" type="button" data-action="open-chat-order" data-id="${order.id}">
                Chat on order
              </button>
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderDeliveryRestaurantSelect() {
  if (!state.restaurants.length) {
    elements.deliveryRestaurantSelect.innerHTML = '<option value="">No restaurants</option>';
    return;
  }

  if (!state.deliveryRestaurantId) {
    state.deliveryRestaurantId = "all";
  }

  elements.deliveryRestaurantSelect.innerHTML = [
    '<option value="all">All restaurants</option>',
    ...state.restaurants.map(
      (restaurant) => `
        <option value="${restaurant.id}" ${restaurant.id === state.deliveryRestaurantId ? "selected" : ""}>
          ${escapeHtml(restaurant.name)}
        </option>
      `,
    ),
  ].join("");
}

function renderDeliveryOrders() {
  if (!state.deliveryOrders.length) {
    elements.deliveryOrdersList.innerHTML =
      '<p class="empty-state">No orders found for this restaurant board yet.</p>';
    return;
  }

  elements.deliveryOrdersList.innerHTML = state.deliveryOrders
    .map((order) => {
      const nextStatus = NEXT_STATUS[order.status];
      return `
        <article class="order-card">
          <div class="order-topline">
            <div>
              <p class="section-label">Delivery queue</p>
              <h4>Order #${escapeHtml(String(order.id).slice(0, 8))}</h4>
            </div>
            <span class="status-badge status-${order.status}">${escapeHtml(order.status)}</span>
          </div>
          <p><strong>Drop-off:</strong> ${escapeHtml(order.delivery_address)}</p>
          <p><strong>Total:</strong> ${formatMoney(order.total_price)}</p>
          <div class="item-list">
            ${order.items
              .map(
                (item) =>
                  `<span class="item-chip">${escapeHtml(`${item.quantity}× ${item.dish_name}`)}</span>`,
              )
              .join("")}
          </div>
          <div class="order-actions">
            <div class="section-actions">
              ${
                nextStatus
                  ? `<button class="secondary-button" type="button" data-action="advance-order" data-id="${order.id}" data-status="${nextStatus}">
                      Mark ${escapeHtml(nextStatus)}
                    </button>`
                  : ""
              }
              <button class="ghost-button" type="button" data-action="open-chat-order" data-id="${order.id}">
                Open chat
              </button>
            </div>
            <span class="muted-text">${escapeHtml(formatDate(order.created_at))}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderProfile() {
  const profile = state.profile || {};
  elements.profileForm.phone.value = profile.phone || "";
  elements.profileForm.avatar_url.value = profile.avatar_url || "";
  elements.profileForm.default_address.value = profile.default_address || "";
}

function syncSelectedCheckoutAddress() {
  if (!state.addresses.length) {
    state.selectedCheckoutAddressId = "";
    return;
  }

  const stillExists = state.addresses.some((address) => address.id === state.selectedCheckoutAddressId);
  if (stillExists) {
    return;
  }

  const defaultAddress = state.addresses.find((address) => address.is_default);
  state.selectedCheckoutAddressId = defaultAddress?.id || state.addresses[0].id;
}

function updateCheckoutState() {
  const hasAddresses = state.addresses.length > 0;
  elements.savedAddressSelect.disabled = !hasAddresses;
  elements.savedAddressSelect.required = hasAddresses;
  elements.checkoutAddressHint.textContent = hasAddresses
    ? "Select one saved address for this order."
    : "Add address first to place an order.";
}

function renderAddressSelect() {
  syncSelectedCheckoutAddress();
  const options = ['<option value="">Select saved address</option>'];

  state.addresses.forEach((address) => {
    options.push(
      `<option value="${address.id}" ${address.id === state.selectedCheckoutAddressId ? "selected" : ""}>${escapeHtml(address.label)}${address.is_default ? " • Default" : ""}</option>`,
    );
  });

  elements.savedAddressSelect.innerHTML = options.join("");
  updateCheckoutState();
}

function renderAddresses() {
  renderAddressSelect();

  if (!state.addresses.length) {
    elements.addressesList.innerHTML = '<p class="empty-state">No saved addresses yet. Add one to make checkout smoother.</p>';
    return;
  }

  elements.addressesList.innerHTML = state.addresses
    .map(
      (address) => `
        <article class="address-card">
          <div>
            <h4>${escapeHtml(address.label)}${address.is_default ? " • Default" : ""}</h4>
            <p>${escapeHtml(address.full_address)}</p>
          </div>
          <div class="section-actions">
            <button class="secondary-button" type="button" data-action="use-address" data-id="${address.id}">
              Use at checkout
            </button>
            <button class="ghost-button" type="button" data-action="delete-address" data-id="${address.id}">
              Delete
            </button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderChatOrderList() {
  const orders = getOrderSource();

  if (!orders.length) {
    elements.chatOrderList.innerHTML = '<p class="empty-state">No related orders available for chat yet.</p>';
    return;
  }

  elements.chatOrderList.innerHTML = orders
    .map((order) => {
      const room = getRoomForOrder(order.id);
      const isActive = order.id === state.activeChatOrderId;
      return `
        <article class="chat-room-item ${isActive ? "active" : ""}">
          <div>
            <strong>${escapeHtml(getRestaurantNameById(order.restaurant_id))}</strong>
            <p class="muted-text">Order #${escapeHtml(String(order.id).slice(0, 8))}</p>
          </div>
          <span class="status-badge status-${order.status}">${escapeHtml(order.status)}</span>
          <p>${escapeHtml(order.delivery_address)}</p>
          <button class="ghost-button" type="button" data-action="open-chat-order" data-id="${order.id}">
            ${room ? "Open conversation" : "Start conversation"}
          </button>
        </article>
      `;
    })
    .join("");
}

function renderChatMessages() {
  if (!state.activeRoom) {
    elements.chatRoomMeta.textContent = "Select an order to start or continue a conversation.";
    elements.chatMessages.innerHTML = '<p class="empty-state">Open an order chat to see messages.</p>';
    return;
  }

  const order = getOrderById(state.activeChatOrderId);
  const restaurantName = order ? getRestaurantNameById(order.restaurant_id) : "Order conversation";
  elements.chatRoomMeta.textContent = `${restaurantName} • Order #${String(state.activeChatOrderId).slice(0, 8)}`;

  if (!state.chatMessages.length) {
    elements.chatMessages.innerHTML = '<p class="empty-state">No messages yet. Send the first update for this order.</p>';
    return;
  }

  elements.chatMessages.innerHTML = state.chatMessages
    .map((message) => {
      const isMine = message.sender_id === state.currentUser?.user_id;
      return `
        <article class="chat-bubble ${isMine ? "mine" : ""} ${message.sender_role === "support" ? "support" : ""}">
          <div class="chat-bubble-head">
            <span>${escapeHtml(capitalize(message.sender_role))}</span>
            <span>${escapeHtml(formatDate(message.created_at))}</span>
          </div>
          <div>${escapeHtml(message.content)}</div>
        </article>
      `;
    })
    .join("");

  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function applySavedAddress(addressId) {
  const address = state.addresses.find((item) => item.id === addressId);
  if (!address) {
    return;
  }
  state.selectedCheckoutAddressId = address.id;
  elements.savedAddressSelect.value = address.id;
  updateCheckoutState();
}

async function loadRestaurants() {
  try {
    state.restaurants = await request(`${API.products}/restaurants`);
    renderDeliveryRestaurantSelect();
    renderRestaurants();
    renderOverview();
    updateWorkspaceMeta();
  } catch (error) {
    elements.restaurantsGrid.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}

async function loadMenu(restaurantId) {
  try {
    const menu = await request(`${API.products}/restaurants/${restaurantId}/menu`);
    state.selectedRestaurant = menu.restaurant;
    state.selectedMenu = menu.dishes;
    renderMenu();
    switchView("menu");
  } catch (error) {
    elements.menuGrid.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}

async function loadOrders() {
  if (!isRole("customer", "admin")) {
    state.orders = [];
    renderOrders();
    renderChatOrderList();
    return;
  }

  try {
    state.orders = await request(API.orders);
  } catch (error) {
    state.orders = [];
    elements.ordersList.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }

  renderOrders();
  renderChatOrderList();
  renderOverview();
  updateWorkspaceMeta();
}

async function loadDeliveryOrders() {
  if (!isRole("courier", "admin")) {
    state.deliveryOrders = [];
    renderDeliveryOrders();
    return;
  }

  if (!state.deliveryRestaurantId && state.restaurants.length) {
    state.deliveryRestaurantId = "all";
  }

  if (!state.deliveryRestaurantId) {
    state.deliveryOrders = [];
    renderDeliveryOrders();
    return;
  }

  try {
    if (state.deliveryRestaurantId === "all") {
      const responses = await Promise.all(
        state.restaurants.map((restaurant) => request(`${API.orders}/restaurant/${restaurant.id}`)),
      );

      const mergedOrders = responses.flat();
      const uniqueOrders = Array.from(new Map(mergedOrders.map((order) => [order.id, order])).values());
      state.deliveryOrders = sortOrdersByCreatedAt(uniqueOrders);
    } else {
      const orders = await request(`${API.orders}/restaurant/${state.deliveryRestaurantId}`);
      state.deliveryOrders = sortOrdersByCreatedAt(orders);
    }
  } catch (error) {
    state.deliveryOrders = [];
    elements.deliveryOrdersList.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }

  renderDeliveryOrders();
  renderChatOrderList();
  renderOverview();
  updateWorkspaceMeta();
}

async function loadProfile() {
  try {
    state.profile = await request(`${API.users}/profile`);
  } catch {
    state.profile = null;
  }

  renderProfile();
}

async function loadAddresses() {
  try {
    state.addresses = await request(`${API.users}/addresses`);
  } catch {
    state.addresses = [];
  }

  renderAddresses();
  renderOverview();
}

async function loadMyRooms() {
  if (!isRole("customer", "courier")) {
    state.rooms = [];
    renderChatOrderList();
    updateWorkspaceMeta();
    return;
  }

  try {
    state.rooms = await request(`${API.chat}/my-rooms`);
  } catch {
    state.rooms = [];
  }

  renderChatOrderList();
  updateWorkspaceMeta();
}

function addToCart(dishId) {
  const dish = state.selectedMenu.find((item) => item.id === dishId);
  if (!dish || !state.selectedRestaurant) {
    return;
  }

  if (state.cart.length && state.cart[0].restaurantId !== state.selectedRestaurant.id) {
    state.cart = [];
    setMessage(elements.orderMessage, "Cart was reset because you switched to a different restaurant.");
  }

  const existing = state.cart.find((item) => item.id === dishId);
  if (existing) {
    existing.quantity += 1;
  } else {
    state.cart.push({
      id: dish.id,
      restaurantId: state.selectedRestaurant.id,
      restaurantName: state.selectedRestaurant.name,
      name: dish.name,
      price: Number(dish.price),
      quantity: 1,
    });
  }

  renderCart();
}

function removeFromCart(dishId) {
  state.cart = state.cart.filter((item) => item.id !== dishId);
  renderCart();
}

function buildAddressPayload(formData) {
  const city = String(formData.get("city") || "").trim();
  const district = String(formData.get("district") || "").trim();
  const street = String(formData.get("street") || "").trim();
  const building = String(formData.get("building") || "").trim();
  const apartment = String(formData.get("apartment") || "").trim();
  const details = String(formData.get("details") || "").trim();

  const parts = [
    city,
    district,
    `${street}${building ? `, ${building}` : ""}`,
    apartment ? `Unit ${apartment}` : "",
    details,
  ].filter(Boolean);

  return {
    label: String(formData.get("label") || "").trim(),
    full_address: parts.join(" • "),
    is_default: formData.get("is_default") === "on",
  };
}

async function ensureChatRoom(order) {
  try {
    const room = await request(`${API.chat}/rooms/${order.id}`);
    syncRoomCache(room);
    return room;
  } catch (error) {
    if (error.status !== 404) {
      throw error;
    }
  }

  if (!isRole("customer")) {
    throw new Error("The customer has not started a chat for this order yet.");
  }

  const room = await request(`${API.chat}/rooms`, {
    method: "POST",
    body: JSON.stringify({
      order_id: order.id,
      customer_id: state.currentUser.user_id,
    }),
  });
  syncRoomCache(room);
  return room;
}

async function openChatForOrder(orderId) {
  const order = getOrderById(orderId);
  if (!order) {
    setMessage(elements.chatMessage, "Order not found for chat.", true);
    return;
  }

  try {
    let room = await ensureChatRoom(order);

    if (isRole("courier") && room.courier_id !== state.currentUser.user_id) {
      room = await request(`${API.chat}/rooms/${room.id}/claim`, { method: "PATCH" });
      syncRoomCache(room);
      await loadMyRooms();
    }

    state.activeChatOrderId = orderId;
    state.activeRoom = room;
    state.chatMessages = await request(`${API.chat}/rooms/${room.id}/messages`);
    await request(`${API.chat}/rooms/${room.id}/read`, { method: "PATCH" });
    renderChatOrderList();
    renderChatMessages();
    switchView("chat");
    setMessage(elements.chatMessage, "");
  } catch (error) {
    setMessage(elements.chatMessage, error.message, true);
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);

  try {
    const data = await request(`${API.auth}/login`, {
      method: "POST",
      body: JSON.stringify({
        email: formData.get("email"),
        password: formData.get("password"),
      }),
    });

    saveSession(data.access_token, {
      user_id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
    });
    setMessage(elements.authMessage, "Login successful.");
    updateAuthUI();
    await bootstrapAuthenticatedArea();
  } catch (error) {
    setMessage(elements.authMessage, error.message, true);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);

  try {
    const data = await request(`${API.auth}/register`, {
      method: "POST",
      body: JSON.stringify({
        full_name: formData.get("full_name"),
        email: formData.get("email"),
        password: formData.get("password"),
      }),
    });

    saveSession(data.access_token, {
      user_id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
    });
    setMessage(elements.authMessage, "Customer account created successfully.");
    updateAuthUI();
    await bootstrapAuthenticatedArea();
  } catch (error) {
    setMessage(elements.authMessage, error.message, true);
  }
}

async function handleProfileSave(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);

  try {
    state.profile = await request(`${API.users}/profile`, {
      method: "PUT",
      body: JSON.stringify({
        phone: formData.get("phone") || null,
        avatar_url: formData.get("avatar_url") || null,
        default_address: formData.get("default_address") || null,
      }),
    });
    renderProfile();
    renderOverview();
    setMessage(elements.orderMessage, "Profile updated.");
  } catch (error) {
    setMessage(elements.orderMessage, error.message, true);
  }
}

async function handleAddressAdd(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);

  try {
    const createdAddress = await request(`${API.users}/addresses`, {
      method: "POST",
      body: JSON.stringify(buildAddressPayload(formData)),
    });
    form.reset();

    if (createdAddress.is_default) {
      state.addresses = state.addresses.map((address) => ({ ...address, is_default: false }));
    }

    state.addresses = [createdAddress, ...state.addresses.filter((address) => address.id !== createdAddress.id)];
    state.selectedCheckoutAddressId = createdAddress.id;
    renderAddresses();
    renderOverview();
    await loadProfile();
    setMessage(elements.orderMessage, "Address saved.");
  } catch (error) {
    setMessage(elements.orderMessage, error.message, true);
  }
}

async function handlePlaceOrder(event) {
  event.preventDefault();

  if (!state.cart.length) {
    setMessage(elements.orderMessage, "Add dishes to your cart before placing an order.", true);
    return;
  }

  if (!state.selectedCheckoutAddressId) {
    setMessage(elements.orderMessage, "Add address first, then select it for checkout.", true);
    return;
  }

  try {
    const selectedAddress = state.addresses.find((address) => address.id === state.selectedCheckoutAddressId);
    if (!selectedAddress) {
      throw new Error("Selected address was not found. Please choose a saved address again.");
    }

    const createdOrder = await request(API.orders, {
      method: "POST",
      body: JSON.stringify({
        restaurant_id: state.cart[0].restaurantId,
        delivery_address: selectedAddress.full_address,
        items: state.cart.map((item) => ({
          dish_id: item.id,
          quantity: item.quantity,
          dish_name: item.name,
          price: item.price,
        })),
      }),
    });

    try {
      const room = await request(`${API.chat}/rooms`, {
        method: "POST",
        body: JSON.stringify({
          order_id: createdOrder.id,
          customer_id: state.currentUser.user_id,
        }),
      });
      syncRoomCache(room);
    } catch (chatError) {
      console.warn("Chat room was not created automatically:", chatError);
    }

    state.cart = [];
    renderCart();
    await Promise.all([loadOrders(), loadMyRooms()]);
    switchView("orders");
    setMessage(elements.orderMessage, "Order placed successfully.");
  } catch (error) {
    setMessage(elements.orderMessage, error.message, true);
  }
}

async function handleSendChat(event) {
  event.preventDefault();

  if (!state.activeRoom) {
    setMessage(elements.chatMessage, "Open an order chat first.", true);
    return;
  }

  const content = elements.chatInput.value.trim();
  if (!content) {
    setMessage(elements.chatMessage, "Type a message before sending.", true);
    return;
  }

  try {
    await request(`${API.chat}/rooms/${state.activeRoom.id}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
    elements.chatInput.value = "";
    state.chatMessages = await request(`${API.chat}/rooms/${state.activeRoom.id}/messages`);
    renderChatMessages();
    setMessage(elements.chatMessage, "Message sent.");
  } catch (error) {
    setMessage(elements.chatMessage, error.message, true);
  }
}

async function deleteAddress(addressId) {
  try {
    await request(`${API.users}/addresses/${addressId}`, { method: "DELETE" });
    await loadAddresses();
    setMessage(elements.orderMessage, "Address removed.");
  } catch (error) {
    setMessage(elements.orderMessage, error.message, true);
  }
}

async function advanceOrderStatus(orderId, nextStatus) {
  try {
    await request(`${API.orders}/${orderId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: nextStatus }),
    });
    await loadDeliveryOrders();
    setMessage(elements.orderMessage, `Order moved to ${nextStatus}.`);
  } catch (error) {
    setMessage(elements.orderMessage, error.message, true);
  }
}

async function bootstrapAuthenticatedArea() {
  applyRoleVisibility();
  updateWorkspaceMeta();

  await loadRestaurants();
  await Promise.all([loadProfile(), loadAddresses(), loadOrders(), loadMyRooms()]);
  if (isRole("courier", "admin")) {
    await loadDeliveryOrders();
  }

  renderMenu();
  renderCart();
  renderChatMessages();
  renderOverview();
  switchView(getDefaultView());
}

function attachEvents() {
  elements.showLogin.addEventListener("click", () => switchAuthMode("login"));
  elements.showRegister.addEventListener("click", () => switchAuthMode("register"));
  elements.loginForm.addEventListener("submit", handleLogin);
  elements.registerForm.addEventListener("submit", handleRegister);
  elements.profileForm.addEventListener("submit", handleProfileSave);
  elements.addressForm.addEventListener("submit", handleAddressAdd);
  elements.checkoutForm.addEventListener("submit", handlePlaceOrder);
  elements.chatForm.addEventListener("submit", handleSendChat);

  elements.refreshRestaurants.addEventListener("click", loadRestaurants);
  elements.refreshOrders.addEventListener("click", loadOrders);
  elements.refreshDeliveries.addEventListener("click", loadDeliveryOrders);

  elements.restaurantSearch.addEventListener("input", (event) => {
    state.restaurantQuery = event.currentTarget.value;
    renderRestaurants();
  });

  elements.deliveryRestaurantSelect.addEventListener("change", (event) => {
    state.deliveryRestaurantId = event.currentTarget.value;
    loadDeliveryOrders();
  });

  elements.savedAddressSelect.addEventListener("change", (event) => {
    state.selectedCheckoutAddressId = event.currentTarget.value;
    applySavedAddress(event.currentTarget.value);
  });

  elements.logoutButton.addEventListener("click", () => {
    clearSession();
    updateAuthUI();
    applyRoleVisibility();
    switchAuthMode("login");
    switchView("overview");
    renderRestaurants();
    renderOrders();
    renderDeliveryOrders();
    renderCart();
    renderAddresses();
    renderChatOrderList();
    renderChatMessages();
    setMessage(elements.orderMessage, "");
    setMessage(elements.chatMessage, "");
  });

  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  document.body.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const action = target.dataset.action;
    const id = target.dataset.id;

    if (action === "open-menu" && id) {
      loadMenu(id);
    }

    if (action === "add-to-cart" && id) {
      addToCart(id);
    }

    if (action === "remove-from-cart" && id) {
      removeFromCart(id);
    }

    if (action === "delete-address" && id) {
      deleteAddress(id);
    }

    if (action === "use-address" && id) {
      applySavedAddress(id);
      switchView("profile");
    }

    if (action === "open-chat-order" && id) {
      openChatForOrder(id);
    }

    if (action === "advance-order" && id && target.dataset.status) {
      advanceOrderStatus(id, target.dataset.status);
    }
  });
}

async function init() {
  attachEvents();
  switchAuthMode("login");
  updateAuthUI();
  applyRoleVisibility();
  renderRestaurants();
  renderMenu();
  renderOrders();
  renderDeliveryOrders();
  renderCart();
  renderAddresses();
  renderChatOrderList();
  renderChatMessages();
  await pollHealth();
  setInterval(pollHealth, 30000);

  if (state.token) {
    try {
      await bootstrapAuthenticatedArea();
    } catch {
      clearSession();
      updateAuthUI();
      applyRoleVisibility();
    }
  }
}

init();
