// this file only handles visuals
// backend calls these functions when it needs some visual changes
// all these can be done via pyodide, I just leave it as a reference for now

// dom elements
const queryInput = document.getElementById('query-input');
const executeBtn = document.getElementById('execute-btn');
const cancelBtn = document.getElementById('cancel-btn');
const clearBtn = document.getElementById('clear-btn');
const tableHead = document.getElementById('table-head');
const tableBody = document.getElementById('table-body');
const statusMessage = document.getElementById('status-message');
const connectionInfo = document.getElementById('connection-info');
const loadingOverlay = document.getElementById('loading-overlay');
const electricWave = document.getElementById('electric-wave');


/**
 * update status message with visual effects
 * @param {string} message - message to show
 * @param {string} type - 'success', 'error', 'warning', 'info'
 */
window.updateStatus = function(message, type = 'info') {
  statusMessage.textContent = message;
  statusMessage.className = `status-${type}`;
  
  // blink effect for errors
  if (type === 'error') {
    statusMessage.style.animation = 'blink 0.5s 3';
    setTimeout(() => {
      statusMessage.style.animation = '';
    }, 1500);
  }
};

/**
 * update connection info and row count
 * @param {number} rowCount - number of rows
 * @param {string} status - connection status
 */
window.updateConnectionInfo = function(rowCount = 0, status = 'ready') {
  connectionInfo.textContent = `rows: ${rowCount} | status: ${status}`;
};

/**
 * show/hide loading overlay with spinner
 * @param {boolean} show - true to show
 */
window.showLoading = function(show = true) {
  if (show) {
    loadingOverlay.classList.add('show');
    triggerElectricWave(); // automatic effect when loading
  } else {
    loadingOverlay.classList.remove('show');
  }
};

/**
 * trigger the electric wave effect
 */
window.triggerElectricWave = function() {
  electricWave.classList.remove('active');
  setTimeout(() => {
    electricWave.classList.add('active');
  }, 10);
};

/**
 * populate table with data and appearing effects
 * @param {Array} headers - column names
 * @param {Array} rows - row data
 */
window.updateTable = function(headers, rows) {
  // fade out effect before updating
  tableHead.style.opacity = '0.3';
  tableBody.style.opacity = '0.3';
  
  setTimeout(() => {
    // clear table
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';

    if (!headers || !rows || rows.length === 0) {
      showEmptyTable();
      return;
    }

    // create headers with staggered animation
    const headerRow = document.createElement('tr');
    headers.forEach((header, index) => {
      const th = document.createElement('th');
      th.textContent = header.toUpperCase();
      th.style.opacity = '0';
      headerRow.appendChild(th);
      
      // staggered header animation
      setTimeout(() => {
        th.style.transition = 'opacity 0.3s ease';
        th.style.opacity = '1';
      }, index * 50);
    });
    tableHead.appendChild(headerRow);

    // create rows with appearing effect
    rows.forEach((rowData, rowIndex) => {
      const tr = document.createElement('tr');
      tr.style.opacity = '0';
      
      const cellValues = Array.isArray(rowData) 
        ? rowData 
        : headers.map(header => rowData[header] || '');
      
      cellValues.forEach(cellData => {
        const td = document.createElement('td');
        td.textContent = cellData || '';
        tr.appendChild(td);
      });
      
      tableBody.appendChild(tr);
      
      // staggered row animation
      setTimeout(() => {
        tr.style.transition = 'opacity 0.4s ease';
        tr.style.opacity = '1';
      }, (rowIndex * 100) + 200);
    });

    // restore container opacity
    setTimeout(() => {
      tableHead.style.opacity = '1';
      tableBody.style.opacity = '1';
    }, 300);

    // update counter
    window.updateConnectionInfo(rows.length, 'connected');
    
    // final success effect
    setTimeout(() => {
      window.triggerElectricWave();
    }, (rows.length * 100) + 500);
    
  }, 200);
};

/**
 * show empty table state
 */
function showEmptyTable() {
  const emptyRow = document.createElement('tr');
  const emptyCell = document.createElement('td');
  emptyCell.textContent = 'no data found';
  emptyCell.colSpan = 8;
  emptyCell.style.textAlign = 'center';
  emptyCell.style.padding = '40px 20px';
  emptyCell.style.color = '#666';
  emptyCell.style.fontStyle = 'italic';
  emptyRow.appendChild(emptyCell);
  tableBody.appendChild(emptyRow);
  
  tableHead.style.opacity = '1';
  tableBody.style.opacity = '1';
  window.updateConnectionInfo(0, 'no results');
}

/**
 * enable/disable buttons with visual effects
 * @param {boolean} disabled - true to disable
 */
window.setButtonsDisabled = function(disabled) {
  executeBtn.disabled = disabled;
  clearBtn.disabled = disabled;
  cancelBtn.disabled = !disabled; // cancel only available when executing
  
  // visual effects on buttons
  if (disabled) {
    executeBtn.style.opacity = '0.5';
    clearBtn.style.opacity = '0.5';
    cancelBtn.style.opacity = '1';
    cancelBtn.style.animation = 'blink 1s infinite';
  } else {
    executeBtn.style.opacity = '1';
    clearBtn.style.opacity = '1';
    cancelBtn.style.opacity = '0.7';
    cancelBtn.style.animation = '';
  }
};

/**
 * get current query from input
 * @returns {string} current query
 */
window.getCurrentQuery = function() {
  return queryInput.value.trim();
};

/**
 * clear input with fade effect
 */
window.clearQueryInput = function() {
  // fade out effect
  queryInput.style.opacity = '0.3';
  setTimeout(() => {
    queryInput.value = '';
    queryInput.style.transition = 'opacity 0.3s ease';
    queryInput.style.opacity = '1';
  }, 150);
};

/**
 * clear entire interface
 */
window.clearInterface = function() {
  window.clearQueryInput();
  showEmptyTable();
  window.updateStatus('interface cleared', 'info');
  window.updateConnectionInfo(0, 'waiting');
};

/**
 * error effect on input field
 */
window.showInputError = function() {
  queryInput.style.borderColor = '#ff0000';
  queryInput.style.boxShadow = 'inset 0 0 10px rgba(255, 0, 0, 0.3)';
  
  setTimeout(() => {
    queryInput.style.borderColor = '#00ff00';
    queryInput.style.boxShadow = 'inset 0 0 5px rgba(0, 255, 0, 0.3)';
  }, 1000);
};

/**
 * success effect on input field
 */
window.showInputSuccess = function() {
  queryInput.style.borderColor = '#00ff00';
  queryInput.style.boxShadow = 'inset 0 0 10px rgba(0, 255, 0, 0.5)';
  
  setTimeout(() => {
    queryInput.style.boxShadow = 'inset 0 0 5px rgba(0, 255, 0, 0.3)';
  }, 1000);
};

/**
 * fullscreen flash effect for important results
 */
window.flashScreen = function(color = '#00ff00', duration = 200) {
  const flash = document.createElement('div');
  flash.style.position = 'fixed';
  flash.style.top = '0';
  flash.style.left = '0';
  flash.style.width = '100%';
  flash.style.height = '100%';
  flash.style.backgroundColor = color;
  flash.style.opacity = '0.1';
  flash.style.pointerEvents = 'none';
  flash.style.zIndex = '9999';
  
  document.body.appendChild(flash);
  
  setTimeout(() => {
    flash.style.transition = `opacity ${duration}ms ease`;
    flash.style.opacity = '0';
    setTimeout(() => {
      document.body.removeChild(flash);
    }, duration);
  }, 50);
};

// automatic system effects 

// occasional screen flicker (retro effect)
setInterval(() => {
  if (Math.random() < 0.05) {
    document.querySelector('.screen').style.opacity = '0.9';
    setTimeout(() => {
      document.querySelector('.screen').style.opacity = '1';
    }, 100);
  }
}, 5000);

// random electric wave (ambient effect)
setInterval(() => {
  if (Math.random() < 0.03) {
    window.triggerElectricWave();
  }
}, 8000);



document.addEventListener('DOMContentLoaded', function() {
  // setup initial ui
  window.updateStatus('system ready', 'success');
  window.updateConnectionInfo(0, 'waiting');
  showEmptyTable();
  
  console.log("ready")
})
