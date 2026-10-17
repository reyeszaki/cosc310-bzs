// All requests use the same-origin API served by FastAPI.
async function apiRequest(url, options) {
  document.getElementById("appMessage").innerText = "";
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body);
    } catch (_) {
      // A server/proxy error may not contain JSON.
    }
    throw new Error(detail);
  }
  return response;
}

function showError(error) {
  document.getElementById("appMessage").innerText = error.message || "Request failed";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

let currentRestaurant = null;

async function loadRestaurants() {
  const search = document.getElementById("searchInput").value.trim();
  const cuisine = document.getElementById("cuisineInput").value.trim();
  const isOpen = document.getElementById("isOpenFilter").value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (cuisine) params.append("cuisine", cuisine);
  if (isOpen !== "") params.append("is_open", isOpen);

  const url = `/restaurants${params.toString() ? "?" + params.toString() : ""}`;

  try {
    const res = await apiRequest(url);
    if (!res.ok) throw new Error("Failed to fetch restaurants");
    const data = await res.json();

    const listDiv = document.getElementById("restaurantList");
    if (data.length === 0) {
      listDiv.innerHTML = "<p>No restaurants found matching your criteria.</p>";
      return;
    }

    listDiv.innerHTML = data.map(r => `
      <div class="card">
        <h3>${escapeHtml(r.name)} (${escapeHtml(r.cuisine)})</h3>
        <p>Address: ${escapeHtml(r.address)}</p>
        <p>Status: <span class="${r.is_open ? 'open' : 'closed'}">${r.is_open ? 'Open' : 'Closed'}</span></p>
        <button onclick="viewDetails(${r.id})">View Details & Menu</button>
        <button class="danger" onclick="deleteRestaurant(${r.id})">Delete</button>
      </div>
    `).join("");
  } catch (err) {
    document.getElementById("restaurantList").innerText = err.message;
  }
}

function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("cuisineInput").value = "";
  document.getElementById("isOpenFilter").value = "";
  loadRestaurants();
}

async function viewDetails(restaurantId) {
  const detailsSec = document.getElementById("detailsSection");
  detailsSec.style.display = "block";
  currentRestaurant = null;
  document.getElementById("restaurantDetails").innerText = "Loading restaurant...";
  document.getElementById("menuItems").innerText = "";
  document.getElementById("menuCategoryFilter").value = "";
  toggleEditRestaurantBox(false);
  closeEditMenuItem();

  try {
    const resRest = await apiRequest(`/restaurants/${restaurantId}`);
    if (!resRest.ok) throw new Error("Could not load restaurant details");
    const restaurant = await resRest.json();
    currentRestaurant = restaurant;

    document.getElementById("restaurantDetails").innerHTML = `
      <div class="card">
        <h3>${escapeHtml(restaurant.name)} (ID: ${restaurant.id})</h3>
        <p><strong>Cuisine:</strong> ${escapeHtml(restaurant.cuisine)} | <strong>Address:</strong> ${escapeHtml(restaurant.address)}</p>
        <p><strong>Status:</strong> <span class="${restaurant.is_open ? 'open' : 'closed'}">${restaurant.is_open ? 'Open' : 'Closed'}</span></p>
        <button onclick="toggleRestaurantStatus()">Set ${restaurant.is_open ? 'Closed' : 'Open'}</button>
        <button onclick="openEditRestaurantBox()">Edit Info</button>
        <button class="danger" onclick="deleteRestaurant(${restaurant.id})">Delete Restaurant</button>
      </div>
    `;

    await loadMenu(restaurantId);
  } catch (err) {
    showError(err);
    document.getElementById("restaurantDetails").innerText = err.message;
  }
}

async function handleCreateRestaurant(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById("newName").value.trim(),
    cuisine: document.getElementById("newCuisine").value.trim(),
    address: document.getElementById("newAddress").value.trim(),
    is_open: document.getElementById("newIsOpen").value === "true"
  };

  try {
    const res = await apiRequest("/restaurants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const msg = document.getElementById("createMessage");
    if (res.ok) {
      msg.style.color = "green";
      msg.innerText = "Restaurant created successfully!";
      document.getElementById("createRestaurantForm").reset();
      loadRestaurants();
    } else {
      const err = await res.json();
      msg.style.color = "red";
      msg.innerText = "Error: " + JSON.stringify(err.detail || err);
    }
  } catch (err) {
    document.getElementById("createMessage").style.color = "red";
    document.getElementById("createMessage").innerText = err.message;
  }
}

function toggleEditRestaurantBox(show) {
  document.getElementById("editRestaurantBox").style.display = show ? "block" : "none";
}

function openEditRestaurantBox() {
  if (!currentRestaurant) return;
  document.getElementById("editRestName").value = currentRestaurant.name;
  document.getElementById("editRestCuisine").value = currentRestaurant.cuisine;
  document.getElementById("editRestAddress").value = currentRestaurant.address;
  document.getElementById("editRestIsOpen").value = String(currentRestaurant.is_open);
  toggleEditRestaurantBox(true);
}

async function handleUpdateRestaurant(event) {
  try {
    event.preventDefault();
    if (!currentRestaurant) return;

    const payload = {
      name: document.getElementById("editRestName").value.trim(),
      cuisine: document.getElementById("editRestCuisine").value.trim(),
      address: document.getElementById("editRestAddress").value.trim(),
      is_open: document.getElementById("editRestIsOpen").value === "true"
    };

    const res = await apiRequest(`/restaurants/${currentRestaurant.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      toggleEditRestaurantBox(false);
      await viewDetails(currentRestaurant.id);
      await loadRestaurants();
    }
  } catch (err) {
    showError(err);
  }
}

async function toggleRestaurantStatus() {
  try {
    if (!currentRestaurant) return;
    const payload = {
      name: currentRestaurant.name,
      cuisine: currentRestaurant.cuisine,
      address: currentRestaurant.address,
      is_open: !currentRestaurant.is_open
    };

    await apiRequest(`/restaurants/${currentRestaurant.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    await viewDetails(currentRestaurant.id);
    await loadRestaurants();
  } catch (err) {
    showError(err);
  }
}

async function deleteRestaurant(restaurantId) {
  try {
    const res = await apiRequest(`/restaurants/${restaurantId}`, {
      method: "DELETE"
    });

    if (res.ok) {
      if (currentRestaurant && currentRestaurant.id === restaurantId) {
        document.getElementById("detailsSection").style.display = "none";
        currentRestaurant = null;
      }
      loadRestaurants();
    }
  } catch (err) {
    showError(err);
  }
}

async function loadMenu(restaurantId, category = "") {
  const menuDiv = document.getElementById("menuItems");
  const params = new URLSearchParams();
  if (category) params.append("category", category);

  const url = `/restaurants/${restaurantId}/menu${params.toString() ? "?" + params.toString() : ""}`;

  try {
    const resMenu = await apiRequest(url);
    if (!resMenu.ok) {
      menuDiv.innerHTML = "<p>No menu found for this restaurant.</p>";
      return;
    }

    const menuData = await resMenu.json();
    const items = menuData.items || [];

    if (items.length === 0) {
      menuDiv.innerHTML = "<p>No menu items found.</p>";
      return;
    }

    menuDiv.innerHTML = items.map(item => {
      const itemJson = encodeURIComponent(JSON.stringify(item)).replace(/'/g, "%27");
      return `
        <div class="card">
          <strong>${escapeHtml(item.name)}</strong> <em>(${escapeHtml(item.category)})</em> - $${Number(item.price).toFixed(2)}
          <p>${escapeHtml(item.description)}</p>
          <p>Available: <span class="${item.is_available ? 'open' : 'closed'}">${item.is_available ? 'Yes' : 'No'}</span></p>
          <button onclick="openEditMenuItem('${itemJson}')">Edit Item</button>
          <button class="danger" onclick="deleteMenuItem(${item.id})">Delete Item</button>
        </div>
      `;
    }).join("");
  } catch (err) {
    menuDiv.innerText = err.message;
    showError(err);
  }
}

function filterCurrentMenu() {
  if (!currentRestaurant) return;
  const category = document.getElementById("menuCategoryFilter").value.trim();
  loadMenu(currentRestaurant.id, category);
}

function clearMenuFilter() {
  if (!currentRestaurant) return;
  document.getElementById("menuCategoryFilter").value = "";
  loadMenu(currentRestaurant.id);
}

async function handleAddMenuItem(event) {
  try {
    event.preventDefault();
    if (!currentRestaurant) return;

    // Strictly match MenuItemCreate schema (extra="forbid")
    const payload = {
      name: document.getElementById("menuItemName").value.trim(),
      description: document.getElementById("menuItemDesc").value.trim(),
      price: parseFloat(document.getElementById("menuItemPrice").value),
      category: document.getElementById("menuItemCategory").value.trim(),
      is_available: document.getElementById("menuItemAvailable").value === "true"
    };

    const msg = document.getElementById("menuAddMessage");

    const res = await apiRequest(`/restaurants/${currentRestaurant.id}/menu/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      msg.style.color = "green";
      msg.innerText = "Menu item added!";
      document.getElementById("addMenuItemForm").reset();
      loadMenu(currentRestaurant.id, document.getElementById("menuCategoryFilter").value.trim());
    } else {
      const err = await res.json();
      msg.style.color = "red";
      msg.innerText = "Error: " + JSON.stringify(err.detail || err);
    }
  } catch (err) {
    showError(err);
  }
}

function openEditMenuItem(encodedItem) {
  const item = JSON.parse(decodeURIComponent(encodedItem));
  document.getElementById("editMenuItemCard").style.display = "block";
  document.getElementById("editMenuItemId").value = item.id;
  document.getElementById("editMenuItemIdDisplay").innerText = "ID: " + item.id;
  document.getElementById("editMenuItemName").value = item.name || "";
  document.getElementById("editMenuItemDesc").value = item.description || "";
  document.getElementById("editMenuItemPrice").value = item.price || 0;
  document.getElementById("editMenuItemCategory").value = item.category || "";
  const isAvail = item.is_available !== undefined ? item.is_available : true;
  document.getElementById("editMenuItemAvailable").value = String(isAvail);
}

function closeEditMenuItem() {
  document.getElementById("editMenuItemCard").style.display = "none";
  document.getElementById("menuEditMessage").innerText = "";
}

async function handleUpdateMenuItem(event) {
  try {
    event.preventDefault();
    if (!currentRestaurant) return;

    const itemId = document.getElementById("editMenuItemId").value;
    const payload = {
      name: document.getElementById("editMenuItemName").value.trim(),
      description: document.getElementById("editMenuItemDesc").value.trim(),
      price: parseFloat(document.getElementById("editMenuItemPrice").value),
      category: document.getElementById("editMenuItemCategory").value.trim(),
      is_available: document.getElementById("editMenuItemAvailable").value === "true"
    };

    const msg = document.getElementById("menuEditMessage");

    // Part C uses PATCH for updating menu items
    const res = await apiRequest(`/restaurants/${currentRestaurant.id}/menu/items/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      closeEditMenuItem();
      loadMenu(currentRestaurant.id, document.getElementById("menuCategoryFilter").value.trim());
    } else {
      const err = await res.json();
      msg.style.color = "red";
      msg.innerText = "Error: " + JSON.stringify(err.detail || err);
    }
  } catch (err) {
    showError(err);
  }
}

async function deleteMenuItem(itemId) {
  try {
    if (!currentRestaurant) return;

    const res = await apiRequest(`/restaurants/${currentRestaurant.id}/menu/items/${itemId}`, {
      method: "DELETE"
    });

    if (res.ok) {
      loadMenu(currentRestaurant.id, document.getElementById("menuCategoryFilter").value.trim());
    }
  } catch (err) {
    showError(err);
  }
}

// Initial load on page startup
loadRestaurants();
