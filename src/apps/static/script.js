// Запуск парсинга
async function parseProducts() {
    const category = document.getElementById('categoryInput').value;

    if (!category) {
        alert("Введите категорию!");
        return;
    }
 
    try {

        const response = await fetch('/api/products/parse_products/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({category})
        });

        const result = await response.json();

        if (response.ok) {
            alert('Товары сохранены.');
            // loadProducts();
        } else {
            alert('Ошибка');
        }
    } catch (error) {
        alert(`Ошибка запроса: ${error}`);
    }
}

// Загрузка товаров с фильтрами
async function loadProducts() {
    // Получаем значения фильтров
    const sortField = document.getElementById('sortField').value;
    const minPrice = document.getElementById('minPrice').value * 100;
    const maxPrice = document.getElementById('maxPrice').value * 100;
    const minRating = document.getElementById('minRating').value;
    const maxRating = document.getElementById('maxRating').value;
    const minFeedbacks = document.getElementById('minFeedbacks').value;
    const maxFeedbacks = document.getElementById('maxFeedbacks').value;

    // Формируем URL с query-параметрами
    const url = new URL('/api/products/', window.location.origin);
    
    // Добавляем параметры сортировки
    if (sortField) {
        url.searchParams.append('o', sortField);  // Используем 'o' для OrderingFilter
    }
    
    // Добавляем параметры фильтрации
    if (minPrice) url.searchParams.append('min_price', minPrice);
    if (maxPrice) url.searchParams.append('max_price', maxPrice);
    if (minRating) url.searchParams.append('min_rating', minRating);
    if (maxRating) url.searchParams.append('max_rating', maxRating);
    if (minFeedbacks) url.searchParams.append('min_feedbacks', minFeedbacks);
    if (maxFeedbacks) url.searchParams.append('max_feedbacks', maxFeedbacks);

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const products = await response.json();
        renderProducts(products);
        renderHistogram(products);
        renderLineChart(products);
    } catch (error) {
        console.error("Ошибка загрузки товаров:", error);
        // Можно добавить отображение ошибки пользователю
        alert('Не удалось загрузить товары. Пожалуйста, попробуйте позже.');
    }
}

// Отрисовка товаров в таблице
function renderProducts(products) {
    const tableBody = document.getElementById('productsBody');
    tableBody.innerHTML = '';

    products.forEach(product => {
        const row = document.createElement('tr');
        // Преобразование чисел
        const priceInRubles = product.price / 100;
        const discounterPriceInRubles = product.discounter_price / 100;
        row.innerHTML = `
            <td>${product.name}</td>
            <td>${priceInRubles}</td>
            <td>${discounterPriceInRubles}</td>
            <td>${product.rating}</td>
            <td>${product.feedbacks}</td>
        `;
        tableBody.appendChild(row);
    });
}

function renderHistogram(products) {
    const prices = products.map(p => p.price / 100);
    
    if (prices.length === 0) return;
    
    // Находим min и max цены
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    
    // Определяем количество интервалов (можно настроить)
    const binCount = 5;
    const binSize = (maxPrice - minPrice) / binCount;
    
    // Массив для подсчета количества товаров в каждом интервале
    const bins = new Array(binCount).fill(0);
    
    // Распределяет товары по интервалам
    prices.forEach(price => {
        let binIndex = Math.floor((price - minPrice) / binSize);
        binIndex = Math.min(binIndex, binCount - 1);
        bins[binIndex]++;
    });
    
    const ctx = document.getElementById('priceHistogram').getContext('2d');
    
    // Вычисляет интервалы
    const labels = [];
    for (let i = 0; i < binCount; i++) {
        const start = minPrice + i * binSize;
        const end = start + binSize;
        labels.push(`${start.toFixed(2)} - ${end.toFixed(2)}`);
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Количество товаров',
                data: bins,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество товаров'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Диапазон цен (руб)'
                    }
                }
            }
        }
    });
}

function renderLineChart(products) {
    const data = products.map(product => {
        // Рассчитывает размер скидки в %
        const discount = ((product.price - product.discounter_price) / product.price * 100).toFixed(1);
        return {
            rating: product.rating,
            discount: parseFloat(discount)
        };
    });

    data.sort((a, b) => a.rating - b.rating);

    // Группиррвка данных по рейтингу
    const groupedData = {};
    data.forEach(item => {
        if (!groupedData[item.rating]) {
            groupedData[item.rating] = {
                rating: item.rating,
                sum: 0,
                count: 0
            };
        }
        groupedData[item.rating].sum += item.discount;
        groupedData[item.rating].count++;
    });

    const labels = [];
    const discounts = [];
    Object.values(groupedData).forEach(item => {
        labels.push(item.rating.toFixed(1));
        discounts.push(item.sum / item.count);
    });

    const ctx = document.getElementById('discountRatingChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Средний размер скидки (%)',
                data: discounts,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Зависимость скидки от рейтинга товара'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Скидка: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Размер скидки (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Рейтинг товара'
                    }
                }
            }
        }
    });
}