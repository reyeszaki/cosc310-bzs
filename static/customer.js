let customerToken = sessionStorage.getItem("customerToken") || "";
let customer = null;
let checkoutBusy = false;

// All customer requests use the same bearer token and error handling.
async function customerRequest(path, method = "GET", data = null, authenticated = true) {
  const headers = {};
  if (authenticated) headers.Authorization = "Bearer " + customerToken;
  if (data !== null) headers["Content-Type"] = "application/json";
  const options = {method: method, headers: headers};
  if (data !== null) options.body = JSON.stringify(data);
  const response = await fetch(path, options);
  if (response.status === 204) return null;
  const result = await response.json();
  if (!response.ok) {
    if (authenticated && response.status === 401) resetCustomer();
    let message = result.detail || "Request failed.";
    if (Array.isArray(message)) message = message.map(error => error.msg).join("; ");
    throw new Error(message);
  }
  return result;
}

function resetCustomer() {
  customerToken = "";
  customer = null;
  sessionStorage.removeItem("customerToken");
  document.getElementById("signInForms").hidden = false;
  document.getElementById("customerAccount").hidden = true;
  document.getElementById("customerShopping").hidden = true;
  document.getElementById("customerCart").replaceChildren();
  document.getElementById("customerOrders").replaceChildren();
  document.getElementById("orderConfirmation").replaceChildren();
  document.getElementById("cartTotal").textContent = "";
  document.getElementById("shoppingMessage").textContent = "";
  document.getElementById("accountStatus").textContent = "Please sign in.";
  document.getElementById("checkoutButton").disabled = true;
  document.getElementById("profileForm").reset();
}

function showCustomerProfile() {
  document.getElementById("signInForms").hidden = true;
  document.getElementById("customerAccount").hidden = false;
  document.getElementById("customerShopping").hidden = customer.role !== "customer";
  document.getElementById("profileName").value = customer.name;
  document.getElementById("profileLastName").value = customer.last_name;
  document.getElementById("profileEmail").value = customer.email;
  document.getElementById("deliveryAddress").value = customer.address || "";
  document.getElementById("accountStatus").textContent = "Signed in as " + customer.name + ".";
}

async function registerCustomer(event) {
  event.preventDefault();
  try {
    await customerRequest("/users", "POST", {
      name: document.getElementById("registerName").value.trim(),
      last_name: document.getElementById("registerLastName").value.trim(),
      email: document.getElementById("registerEmail").value.trim(),
      password: document.getElementById("registerPassword").value
    }, false);
    document.getElementById("registerForm").reset();
    document.getElementById("accountStatus").textContent = "Account created. Sign in to continue.";
  } catch (error) {
    document.getElementById("accountStatus").textContent = error.message;
  }
}

async function loginCustomer(event) {
  event.preventDefault();
  try {
    const result = await customerRequest("/auth/login", "POST", {
      email: document.getElementById("loginEmail").value.trim(),
      password: document.getElementById("loginPassword").value
    }, false);
    customerToken = result.access_token;
    sessionStorage.setItem("customerToken", customerToken);
    customer = result.user;
    document.getElementById("loginForm").reset();
    showCustomerProfile();
    if (customer.role === "customer") {
      await loadCustomerCart();
      await loadCustomerOrders();
    }
  } catch (error) {
    document.getElementById("accountStatus").textContent = error.message;
  }
}

async function saveCustomerProfile(event) {
  event.preventDefault();
  try {
    customer = await customerRequest("/users/me", "PUT", {
      name: document.getElementById("profileName").value.trim(),
      last_name: document.getElementById("profileLastName").value.trim(),
      email: document.getElementById("profileEmail").value.trim(),
      address: document.getElementById("deliveryAddress").value.trim()
    });
    showCustomerProfile();
    document.getElementById("accountStatus").textContent = "Profile and address saved.";
  } catch (error) {
    document.getElementById("accountStatus").textContent = error.message;
  }
}

async function logoutCustomer() {
  try {
    await customerRequest("/auth/logout", "POST");
    resetCustomer();
    document.getElementById("accountStatus").textContent = "Signed out.";
  } catch (error) {
    document.getElementById("accountStatus").textContent = error.message;
  }
}

async function deactivateCustomer() {
  if (!confirm("Deactivate your account? You will no longer be able to sign in.")) return;
  try {
    await customerRequest("/users/me/deactivate", "POST");
    resetCustomer();
    document.getElementById("accountStatus").textContent = "Account deactivated.";
  } catch (error) {
    document.getElementById("accountStatus").textContent = error.message;
  }
}

function showCustomerCart(cart) {
  const container = document.getElementById("customerCart");
  container.replaceChildren();
  for (const item of cart.items) {
    const row = document.createElement("div");
    row.className = "card";
    const details = document.createElement("p");
    details.textContent = item.name + " — $" + Number(item.unit_price).toFixed(2) + " each; line total $" + Number(item.line_total).toFixed(2);
    const label = document.createElement("label");
    label.textContent = "Quantity: ";
    const quantity = document.createElement("input");
    quantity.type = "number";
    quantity.min = "1";
    quantity.step = "1";
    quantity.value = item.quantity;
    label.append(quantity);
    const update = document.createElement("button");
    update.textContent = "Update Quantity";
    update.onclick = () => updateCustomerQuantity(item.menu_item_id, quantity.value);
    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.onclick = () => changeCustomerCart("/cart/items/" + item.menu_item_id, "DELETE");
    row.append(details, label, update, remove);
    container.append(row);
  }
  if (!cart.items.length) container.textContent = "Your cart is empty.";
  document.getElementById("cartTotal").textContent = "Backend total: $" + Number(cart.total).toFixed(2);
  document.getElementById("checkoutButton").disabled = checkoutBusy || cart.items.length === 0;
}

async function loadCustomerCart() {
  document.getElementById("checkoutButton").disabled = true;
  try {
    showCustomerCart(await customerRequest("/cart"));
  } catch (error) {
    document.getElementById("customerCart").textContent = "Cart could not be loaded. You can clear it and add items again.";
    document.getElementById("cartTotal").textContent = "";
    document.getElementById("shoppingMessage").textContent = error.message;
  }
}

async function changeCustomerCart(path, method, data = null) {
  if (checkoutBusy) return;
  try {
    const cart = await customerRequest(path, method, data);
    showCustomerCart(cart);
    document.getElementById("shoppingMessage").textContent = "Cart updated.";
  } catch (error) {
    document.getElementById("shoppingMessage").textContent = error.message;
  }
}

async function addToCustomerCart(restaurantId, itemId) {
  if (!customer || customer.role !== "customer") {
    document.getElementById("accountStatus").textContent = "Sign in as a customer to add items.";
    return;
  }
  await changeCustomerCart("/cart/items", "POST", {
    restaurant_id: restaurantId, menu_item_id: itemId, quantity: 1
  });
}

async function updateCustomerQuantity(itemId, value) {
  const quantity = Number(value);
  if (!Number.isInteger(quantity) || quantity < 1) {
    document.getElementById("shoppingMessage").textContent = "Enter a positive whole-number quantity.";
    return;
  }
  await changeCustomerCart("/cart/items/" + itemId, "PATCH", {quantity: quantity});
}

async function clearCustomerCart() {
  await changeCustomerCart("/cart/items", "DELETE");
}

function appendOrder(container, order) {
  const card = document.createElement("div");
  card.className = "card";
  const title = document.createElement("h3");
  title.textContent = "Order #" + order.id + " — " + order.status;
  const details = document.createElement("p");
  details.textContent = "Restaurant #" + order.restaurant_id + " | " + new Date(order.created_at).toLocaleString() + " | Total: $" + Number(order.total).toFixed(2);
  const address = document.createElement("p");
  address.textContent = "Delivery address: " + order.delivery_address;
  card.append(title, details, address);
  for (const item of order.items) {
    const line = document.createElement("p");
    line.textContent = item.quantity + " × " + item.name + " — $" + Number(item.line_total).toFixed(2);
    card.append(line);
  }
  container.append(card);
}

async function loadCustomerOrders() {
  const container = document.getElementById("customerOrders");
  try {
    const orders = await customerRequest("/orders");
    container.replaceChildren();
    orders.sort((a, b) => b.id - a.id);
    for (const order of orders) appendOrder(container, order);
    if (!orders.length) container.textContent = "No orders yet.";
  } catch (error) {
    container.textContent = error.message;
  }
}

async function checkoutCustomer() {
  if (checkoutBusy) return;
  checkoutBusy = true;
  document.getElementById("checkoutButton").disabled = true;
  document.getElementById("shoppingMessage").textContent = "Placing your order...";
  let saved = false;
  try {
    const order = await customerRequest("/checkout", "POST");
    saved = true;
    const confirmation = document.getElementById("orderConfirmation");
    confirmation.replaceChildren();
    appendOrder(confirmation, order);
    document.getElementById("shoppingMessage").textContent = "Order placed successfully.";
    await loadCustomerOrders();
  } catch (error) {
    document.getElementById("shoppingMessage").textContent = error.message + " Refresh your orders before retrying.";
  } finally {
    checkoutBusy = false;
    if (customerToken) {
      await loadCustomerCart();
      // After an uncertain failure, require checking orders before another attempt.
      if (!saved) document.getElementById("checkoutButton").disabled = true;
    }
  }
}

async function restoreCustomer() {
  if (!customerToken) return;
  try {
    customer = await customerRequest("/users/me");
    showCustomerProfile();
    if (customer.role === "customer") {
      await loadCustomerCart();
      await loadCustomerOrders();
    }
  } catch (error) {
    resetCustomer();
    document.getElementById("accountStatus").textContent = error.message;
  }
}

restoreCustomer();
