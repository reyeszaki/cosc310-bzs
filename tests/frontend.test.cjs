// Run with: node --test tests/frontend.test.cjs (no npm packages required).
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');

function frontend(fetch) {
  const elements = new Map();
  const context = vm.createContext({
    URLSearchParams, console, fetch,
    document: { getElementById(id) {
      if (!elements.has(id)) elements.set(id, {value:'', innerText:'', innerHTML:'', style:{}, reset(){}});
      return elements.get(id);
    } },
  });
  // Initial page loading is covered by the browser check, not by these isolated regressions.
  vm.runInContext(source.replace(/loadRestaurants\(\);\s*$/, ''), context);
  return { context, element: id=>context.document.getElementById(id), run: code=>vm.runInContext(code, context) };
}

const response = body => ({ok:true, json:async()=>body});

test('item text is literal and apostrophes do not break the edit handler', async()=>{
  const item={id:2,restaurant_id:1,name:"Chef's <b>Tea</b>",description:'Hot & fresh',category:'drinks',price:3.25,is_available:false};
  const ui=frontend(async()=>response({items:[item]}));
  await ui.run('loadMenu(1)');
  const html=ui.element('menuItems').innerHTML;
  assert.ok(html.includes("Chef&#39;s &lt;b&gt;Tea&lt;/b&gt;"));
  const handler=html.match(/onclick="(openEditMenuItem\([^"]+\))"/)[1];
  ui.run(handler);
  assert.equal(ui.element('editMenuItemName').value,item.name);
});

test('failed mutation shows backend detail and does not pretend success', async()=>{
  const ui=frontend(async()=>({ok:false,status:409,json:async()=>({detail:'Remove menu items first'})}));
  await ui.run('deleteRestaurant(1)');
  assert.equal(ui.element('appMessage').innerText,'Remove menu items first');
});

test('network failure is visible instead of becoming an unhandled rejection', async()=>{
  const ui=frontend(async()=>{throw new Error('Network unavailable');});
  await ui.run('deleteRestaurant(1)');
  assert.equal(ui.element('appMessage').innerText,'Network unavailable');
});

test('non-JSON server error has a usable fallback message', async()=>{
  const ui=frontend(async()=>({ok:false,status:500,json:async()=>{throw new Error('HTML body');}}));
  await ui.run('deleteRestaurant(1)');
  assert.equal(ui.element('appMessage').innerText,'Request failed (500)');
});

test('failed details request clears the previously selected restaurant', async()=>{
  const ui=frontend(async()=>({ok:false,status:404,json:async()=>({detail:'Restaurant missing'})}));
  ui.run('currentRestaurant = {id:1};');
  await ui.run('viewDetails(99)');
  assert.equal(ui.run('currentRestaurant'),null);
  assert.equal(ui.element('restaurantDetails').innerText,'Restaurant missing');
});
