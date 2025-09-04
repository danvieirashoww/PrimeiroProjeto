const display = document.getElementById('display');
const historyDiv = document.getElementById('history');
const buttons = document.querySelectorAll('.buttons button');
const themeBtn = document.getElementById('theme-toggle');

let expression = '';
let history = [];

function updateDisplay() {
  display.textContent = expression || '0';
}

function updateHistory() {
  historyDiv.innerHTML = history.map(item => `<div>${item}</div>`).join('');
}

function addToExpression(value) {
  expression += value;
  updateDisplay();
}

function clearAll() {
  expression = '';
  history = [];
  updateDisplay();
  updateHistory();
}

function clearEntry() {
  expression = '';
  updateDisplay();
}

function backspace() {
  expression = expression.slice(0, -1);
  updateDisplay();
}

function toggleSign() {
  if (expression.startsWith('-')) {
    expression = expression.slice(1);
  } else {
    expression = expression ? '-' + expression : expression;
  }
  updateDisplay();
}

function percent() {
  try {
    const value = evaluateExpression(expression) / 100;
    expression = String(value);
    updateDisplay();
  } catch (e) {
    display.textContent = 'Erro';
  }
}

function calculate() {
  try {
    const result = evaluateExpression(expression);
    history.push(`${expression} = ${result}`);
    expression = String(result);
    updateDisplay();
    updateHistory();
  } catch (e) {
    display.textContent = 'Erro';
  }
}

buttons.forEach(btn => {
  const value = btn.getAttribute('data-value');
  const action = btn.getAttribute('data-action');
  if (value) {
    btn.addEventListener('click', () => addToExpression(value));
  } else if (action) {
    btn.addEventListener('click', () => handleAction(action));
  }
});

function handleAction(action) {
  switch (action) {
    case 'clear':
      clearAll();
      break;
    case 'clear-entry':
      clearEntry();
      break;
    case 'backspace':
      backspace();
      break;
    case 'toggle-sign':
      toggleSign();
      break;
    case 'percent':
      percent();
      break;
    case 'divide':
      addToExpression('/');
      break;
    case 'multiply':
      addToExpression('*');
      break;
    case 'subtract':
      addToExpression('-');
      break;
    case 'add':
      addToExpression('+');
      break;
    case 'equals':
      calculate();
      break;
  }
}

function evaluateExpression(expr) {
  const tokens = tokenize(expr);
  const rpn = toRPN(tokens);
  return evalRPN(rpn);
}

function tokenize(expr) {
  const tokens = [];
  let num = '';
  for (let ch of expr) {
    if (/\d|\./.test(ch)) {
      num += ch;
    } else if ('+-*/()%'.includes(ch)) {
      if (num) {
        tokens.push(num);
        num = '';
      }
      tokens.push(ch);
    } else if (ch !== ' ') {
      throw new Error('Invalid');
    }
  }
  if (num) tokens.push(num);
  return tokens;
}

function toRPN(tokens) {
  const output = [];
  const ops = [];
  const prec = { '+': 1, '-': 1, '*': 2, '/': 2, '%': 2 };
  tokens.forEach(t => {
    if (!isNaN(t)) {
      output.push(parseFloat(t));
    } else if (t in prec) {
      while (ops.length && prec[ops[ops.length - 1]] >= prec[t]) {
        output.push(ops.pop());
      }
      ops.push(t);
    } else if (t === '(') {
      ops.push(t);
    } else if (t === ')') {
      while (ops.length && ops[ops.length - 1] !== '(') {
        output.push(ops.pop());
      }
      if (ops.pop() !== '(') throw new Error('Parênteses');
    }
  });
  while (ops.length) {
    const op = ops.pop();
    if (op === '(') throw new Error('Parênteses');
    output.push(op);
  }
  return output;
}

function evalRPN(rpn) {
  const stack = [];
  rpn.forEach(token => {
    if (typeof token === 'number') {
      stack.push(token);
    } else {
      const b = stack.pop();
      const a = stack.pop();
      if (a === undefined || b === undefined) throw new Error('Erro');
      switch (token) {
        case '+': stack.push(a + b); break;
        case '-': stack.push(a - b); break;
        case '*': stack.push(a * b); break;
        case '/': stack.push(a / b); break;
        case '%': stack.push(a % b); break;
      }
    }
  });
  if (stack.length !== 1) throw new Error('Erro');
  return stack[0];
}

function handleKey(e) {
  const key = e.key;
  if (/\d/.test(key)) {
    addToExpression(key);
  } else if (key === '.') {
    addToExpression('.');
  } else if (['+', '-', '*', '/', '%', '(', ')'].includes(key)) {
    addToExpression(key);
  } else if (key === 'Enter') {
    e.preventDefault();
    calculate();
  } else if (key === 'Backspace') {
    backspace();
  } else if (key === 'Escape') {
    clearAll();
  }
}

document.addEventListener('keydown', handleKey);

function applyTheme(theme) {
  if (theme === 'dark') {
    document.body.classList.add('dark');
    themeBtn.textContent = '☀️';
  } else {
    document.body.classList.remove('dark');
    themeBtn.textContent = '🌙';
  }
}

function toggleTheme() {
  const current = document.body.classList.contains('dark') ? 'dark' : 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem('theme', next);
}

themeBtn.addEventListener('click', toggleTheme);
applyTheme(localStorage.getItem('theme') || 'light');

updateDisplay();
