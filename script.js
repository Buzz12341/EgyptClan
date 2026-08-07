/**
 * ============================================================
 * КЛАН ЕГИПЕТ — JavaScript для GitHub Pages
 * ============================================================
 * Функционал:
 *   - Плавная прокрутка к якорям
 *   - Уведомления (toast)
 *   - Копирование ссылок в буфер обмена
 *   - Анимация появления при скролле (Intersection Observer)
 *   - Индикатор загрузки страницы
 *   - Адаптивное меню (бургер)
 *   - Обработка кликов по карточкам
 * ============================================================
 */

(function() {
    'use strict';

    // ============================================================
    // 1. СОСТОЯНИЕ
    // ============================================================
    const state = {
        isReady: false,
        scrollOffset: 80, // отступ для якорей (высота шапки)
        toastTimer: null,
        menuOpen: false,
    };

    // ============================================================
    // 2. DOM-СЕЛЕКТОРЫ
    // ============================================================
    const $ = (selector, context = document) => context.querySelector(selector);
    const $$ = (selector, context = document) => [...context.querySelectorAll(selector)];

    const DOM = {
        body: document.body,
        header: $('.header'),
        hero: $('.hero'),
        cards: $$('.btn-card'),
        rows: $$('.btn-row'),
        infoBlocks: $$('.info-block'),
        footer: $('.footer'),
        // для анимаций появления
        animatedElements: $$('.anim-fade-up, .btn-card, .btn-row, .info-block, .hero-stat'),
    };

    // ============================================================
    // 3. УТИЛИТЫ
    // ============================================================
    const Utils = {
        /** Дебаунс для оптимизации событий */
        debounce(fn, delay = 150) {
            let timer;
            return function(...args) {
                clearTimeout(timer);
                timer = setTimeout(() => fn.apply(this, args), delay);
            };
        },

        /** Форматирование времени */
        formatTime(date) {
            return date.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },

        /** Генерация уникального ID */
        uid() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 6);
        },

        /** Проверка, виден ли элемент */
        isVisible(el, threshold = 0.1) {
            if (!el) return false;
            const rect = el.getBoundingClientRect();
            const height = window.innerHeight || document.documentElement.clientHeight;
            const width = window.innerWidth || document.documentElement.clientWidth;
            const visibleHeight = Math.min(rect.bottom, height) - Math.max(rect.top, 0);
            const visibleWidth = Math.min(rect.right, width) - Math.max(rect.left, 0);
            const visibleArea = visibleHeight * visibleWidth;
            const totalArea = rect.height * rect.width;
            return visibleArea / totalArea > threshold;
        }
    };

    // ============================================================
    // 4. TOAST / УВЕДОМЛЕНИЯ
    // ============================================================
    class Toast {
        constructor() {
            this.container = null;
            this.init();
        }

        init() {
            if (this.container) return;
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.style.cssText = `
                        position: fixed;
                        bottom: 24px;
                        right: 24px;
                        z-index: 9999;
                        display: flex;
                        flex-direction: column;
                        gap: 12px;
                        max-width: 380px;
                        width: 100%;
                        pointer-events: none;
                    `;
            document.body.appendChild(this.container);
        }

        show(message, type = 'info', duration = 3500) {
            const toast = document.createElement('div');
            const colors = {
                info: 'rgba(212, 168, 75, 0.15)',
                success: 'rgba(76, 175, 80, 0.2)',
                error: 'rgba(244, 67, 54, 0.2)',
                warning: 'rgba(255, 152, 0, 0.2)',
            };
            const borderColors = {
                info: '#d4a84b',
                success: '#4CAF50',
                error: '#f44336',
                warning: '#ff9800',
            };

            toast.style.cssText = `
                        background: rgba(28, 22, 16, 0.95);
                        backdrop-filter: blur(12px);
                        -webkit-backdrop-filter: blur(12px);
                        border: 1px solid ${borderColors[type] || '#d4a84b'};
                        border-radius: 14px;
                        padding: 16px 20px;
                        color: #f0e6d8;
                        font-size: 14px;
                        font-family: 'Inter', sans-serif;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
                        transform: translateX(calc(100% + 40px));
                        opacity: 0;
                        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
                        pointer-events: auto;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        position: relative;
                        overflow: hidden;
                    `;

            // Индикатор прогресса
            const progress = document.createElement('div');
            progress.style.cssText = `
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        height: 3px;
                        background: ${borderColors[type] || '#d4a84b'};
                        width: 100%;
                        transition: width ${duration}ms linear;
                    `;
            toast.appendChild(progress);

            // Иконка
            const iconMap = {
                info: 'ℹ️',
                success: '✅',
                error: '❌',
                warning: '⚠️',
            };
            const iconSpan = document.createElement('span');
            iconSpan.textContent = iconMap[type] || 'ℹ️';
            iconSpan.style.fontSize = '20px';
            toast.appendChild(iconSpan);

            // Текст
            const textSpan = document.createElement('span');
            textSpan.textContent = message;
            textSpan.style.flex = '1';
            toast.appendChild(textSpan);

            // Кнопка закрытия
            const closeBtn = document.createElement('button');
            closeBtn.textContent = '✕';
            closeBtn.style.cssText = `
                        background: none;
                        border: none;
                        color: #7a6e62;
                        font-size: 16px;
                        cursor: pointer;
                        padding: 4px 8px;
                        transition: color 0.2s;
                        pointer-events: auto;
                    `;
            closeBtn.addEventListener('mouseenter', () => closeBtn.style.color = '#f0e6d8');
            closeBtn.addEventListener('mouseleave', () => closeBtn.style.color = '#7a6e62');
            closeBtn.addEventListener('click', () => this.hide(toast));
            toast.appendChild(closeBtn);

            this.container.appendChild(toast);

            // Анимация появления
            requestAnimationFrame(() => {
                toast.style.transform = 'translateX(0)';
                toast.style.opacity = '1';
                // Запускаем прогресс
                setTimeout(() => {
                    progress.style.width = '0%';
                }, 50);
            });

            // Авто-скрытие
            const timer = setTimeout(() => {
                this.hide(toast);
            }, duration);

            // Останавливаем таймер при наведении
            toast.addEventListener('mouseenter', () => {
                clearTimeout(timer);
                progress.style.transition = 'none';
                progress.style.width = '100%';
            });

            toast.addEventListener('mouseleave', () => {
                const remaining = duration - (Date.now() - startTime);
                if (remaining > 0) {
                    progress.style.transition = `width ${remaining}ms linear`;
                    progress.style.width = '0%';
                    setTimeout(() => this.hide(toast), remaining);
                }
            });

            const startTime = Date.now();

            return toast;
        }

        hide(toast) {
            if (!toast || !toast.parentNode) return;
            toast.style.transform = 'translateX(calc(100% + 40px))';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 500);
        }

        info(message, duration) { return this.show(message, 'info', duration); }
        success(message, duration) { return this.show(message, 'success', duration); }
        error(message, duration) { return this.show(message, 'error', duration); }
        warning(message, duration) { return this.show(message, 'warning', duration); }
    }

    // ============================================================
    // 5. ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ
    // ============================================================
    class EgyptClanApp {
        constructor() {
            this.toast = new Toast();
            this.observer = null;
            this.init();
        }

        init() {
            // Показываем приветствие
            console.log('🏛️ Клан Египет — сайт загружен');

            // Настройка Intersection Observer для анимаций
            this.setupScrollAnimations();

            // Настройка обработчиков
            this.setupEventListeners();

            // Копирование ссылок
            this.setupCopyLinks();

            // Плавная прокрутка
            this.setupSmoothScroll();

            // Обработка кликов по карточкам
            this.setupCardClicks();

            // Индикатор загрузки
            this.hideLoader();

            // Отметка о готовности
            state.isReady = true;

            // Приветственный тост (с задержкой)
            setTimeout(() => {
                this.toast.info('🏛️ Добро пожаловать в клан Египет!', 3000);
            }, 800);
        }

        // ============================================================
        // SCROLL АНИМАЦИИ (Intersection Observer)
        // ============================================================
        setupScrollAnimations() {
            const elements = DOM.animatedElements;

            if ('IntersectionObserver' in window) {
                this.observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0) scale(1)';
                            // Убираем observer, чтобы не отслеживать повторно
                            this.observer.unobserve(entry.target);
                        }
                    });
                }, {
                    threshold: 0.12,
                    rootMargin: '0px 0px -40px 0px',
                });

                elements.forEach(el => {
                    // Если элемент уже виден — сразу показываем
                    if (Utils.isVisible(el, 0.1)) {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0) scale(1)';
                    } else {
                        el.style.opacity = '0';
                        el.style.transform = 'translateY(30px) scale(0.97)';
                        el.style.transition = 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
                        this.observer.observe(el);
                    }
                });
            } else {
                // fallback для старых браузеров
                elements.forEach(el => {
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            }
        }

        // ============================================================
        // СОБЫТИЯ
        // ============================================================
        setupEventListeners() {
            // Ресайз с дебаунсом
            window.addEventListener('resize', Utils.debounce(() => {
                // Обновляем позиции
            }, 200));

            // Скролл с дебаунсом
            window.addEventListener('scroll', Utils.debounce(() => {
                this.updateHeaderShadow();
            }, 50));

            // Первоначальная проверка
            this.updateHeaderShadow();

            // Клавиатурные сокращения
            document.addEventListener('keydown', (e) => {
                // ESC — закрываем всё
                if (e.key === 'Escape') {
                    // Закрываем возможные попапы
                }
                // Ctrl+Shift+C — копировать ссылку на страницу
                if (e.ctrlKey && e.shiftKey && (e.key === 'C' || e.key === 'c')) {
                    e.preventDefault();
                    const url = window.location.href;
                    this.copyToClipboard(url, 'Ссылка на сайт скопирована!');
                }
            });

            // Обработка ошибок загрузки изображений
            document.addEventListener('error', (e) => {
                if (e.target.tagName === 'IMG') {
                    e.target.style.display = 'none';
                }
            }, true);
        }

        // ============================================================
        // ОБНОВЛЕНИЕ ТЕНИ ШАПКИ ПРИ СКРОЛЛЕ
        // ============================================================
        updateHeaderShadow() {
            const header = DOM.header;
            if (!header) return;
            const scrollY = window.scrollY || window.pageYOffset;
            if (scrollY > 50) {
                header.style.boxShadow = '0 4px 60px rgba(0, 0, 0, 0.9), 0 2px 20px rgba(212, 168, 75, 0.08)';
            } else {
                header.style.boxShadow = '0 4px 40px rgba(0, 0, 0, 0.7)';
            }
        }

        // ============================================================
        // КОПИРОВАНИЕ ССЫЛОК
        // ============================================================
        setupCopyLinks() {
            // Копирование ссылки на страницу при клике на хедере (лого)
            const logo = $('.header h1') || $('.header .logo');
            if (logo) {
                logo.style.cursor = 'pointer';
                logo.addEventListener('click', () => {
                    const url = window.location.href;
                    this.copyToClipboard(url, '🔗 Ссылка на сайт скопирована!');
                });
            }

            // Копирование ссылок с карточек (дополнительно)
            DOM.cards.forEach(card => {
                const link = card.getAttribute('href');
                if (link && link.startsWith('http')) {
                    card.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        this.copyToClipboard(link, '🔗 Ссылка скопирована!');
                    });
                }
            });
        }

        copyToClipboard(text, successMessage = 'Скопировано!') {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text)
                    .then(() => {
                        this.toast.success(successMessage, 2000);
                    })
                    .catch(() => {
                        this.fallbackCopy(text, successMessage);
                    });
            } else {
                this.fallbackCopy(text, successMessage);
            }
        }

        fallbackCopy(text, successMessage) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.toast.success(successMessage, 2000);
            } catch (err) {
                this.toast.error('Не удалось скопировать', 2000);
            }
            document.body.removeChild(textarea);
        }

        // ============================================================
        // ПЛАВНАЯ ПРОКРУТКА
        // ============================================================
        setupSmoothScroll() {
            // Все ссылки с якорями
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const targetId = anchor.getAttribute('href');
                    if (targetId === '#') return;
                    const target = document.querySelector(targetId);
                    if (target) {
                        e.preventDefault();
                        const offset = state.scrollOffset;
                        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                        window.scrollTo({ top, behavior: 'smooth' });
                        // Обновляем URL без перезагрузки
                        history.pushState(null, null, targetId);
                    }
                });
            });
        }

        // ============================================================
        // КЛИКИ ПО КАРТОЧКАМ
        // ============================================================
        setupCardClicks() {
            DOM.cards.forEach(card => {
                card.addEventListener('click', (e) => {
                    // Если внутри есть ссылка — не мешаем
                    if (e.target.closest('a')) return;

                    const link = card.getAttribute('href');
                    if (link && link.startsWith('http')) {
                        // Анимация клика
                        card.style.transform = 'scale(0.96)';
                        setTimeout(() => {
                            card.style.transform = '';
                        }, 150);

                        // Открываем в новой вкладке
                        setTimeout(() => {
                            window.open(link, '_blank');
                        }, 200);
                    }
                });
            });
        }

        // ============================================================
        // ИНДИКАТОР ЗАГРУЗКИ
        // ============================================================
        hideLoader() {
            const loader = document.getElementById('loader') || document.querySelector('.loader');
            if (loader) {
                loader.style.opacity = '0';
                loader.style.transition = 'opacity 0.6s';
                setTimeout(() => {
                    loader.style.display = 'none';
                }, 600);
            }

            // Показываем контент
            document.body.style.opacity = '1';
        }

        // ============================================================
        // ПУБЛИЧНЫЕ МЕТОДЫ
        // ============================================================
        showToast(message, type = 'info', duration) {
            return this
