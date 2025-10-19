# Тренировочный репозиторий: 1
## Из чего состоит
* simple app (ui + nginx + backend + database)
* observability (monitoring, tracing, logging)
* load testing (нагрузочное тестирование)
* docker
![alt text](images/Схема.drawio.png)

## Стек
* backend: Golang
* frontend: HTML, JavaScript
* web-server: NGINX
* database: PostgreSQL
* containerization: Docker
* monitoring: Prometheus
* prometheus-exporters
    * метрики сервера: node-exporter
    * метрики БД: postgres-exporter
    * метрики контейнеров: cAdvisor
* visualization: Grafana
* load testing: k6

## Как запустить
1. Сделайте Fork репозитория
2. Откройте терминал
3. Склонируйте репозиторий локально. Например, для репозитория в моем аккаунте я выполню команду
```bash
git clone https://github.com/nikolaysavelev/system-design-practice-hse-miem-25-26.git
```
4. Перейдите в нужную директорию, выполнив команду
```bash
cd system-design-practice-hse-miem-25-26
```
5. Установите и запустите Docker
6. Внутри директории в терминале выполните команду
```bash
docker-compose up -d --build
```
7. Спустя 15-20 секунд после завершения в терминале выполните команду
```bash
docker ps
```
8. Ожидаем, что в колонке STATUS у всех контейнеров будет состояние "Up ..."

## Проверка корректности развертывания
### Приложение
1. Перейдите в браузере по адресу: http://localhost:8080/
2. Откройте devtools (Инструменты разработчика), вкладка Network
3. В форме напишите Имя + Эмейл и нажмите кнопку "Create"
4. Появится окно, подтверждающее успешную отправку HTTP-запроса и в devtools появится запрос users со статусом 200
5. Убедиться в корректности можно в логах nginx по команде
```bash
docker logs system-design-practice-hse-miem-25-26-nginx-1
```

### База данных
1. Скачайте DBeaver Community / иной графический редактор БД (например, плагин в вашей IDE) / psql для терминала
2. Подключитесь к БД со следующим URL, логопасс demo
```
jdbc:postgresql://localhost:5432/demo
```
3. Найдите таблицу users, ожидаем, что в ней будет ваша запись

### Observability
1. Перейдите на http://localhost:9090/query - ожидаем, что в браузере откроется интерфейс Prometheus.
2. Перейдите на http://localhost:9090/targets - ожидаем, что в списке есть все экспортеры из конфигурации prometheus.yml из репозитория и они светятся зеленым (healthcheck соединений)
3. Перейдите на http://localhost:3000/login - логопасс admin/admin
4. Перейдите в Configuration -> Data sources -> Add data source -> Prometheus
5. В URL введите http://prometheus:9090
6. Нажмите Save & Test, ожидаем, что будет плашка "Data source is working"
7. На вкладке Dashboards перейдите в 
Node Exporter Full, ожидаем, что будет отображаться что-то вроде:
![alt text](images/image.png)
8. Если дашбордов не будет после деплоя, можно найти их в директории dashboards и выполнить импорт json файлов ЛИБО импортировать с официального сайта:
* Node Exporter Full
* k6 dashboard
* postgres exporter dashboard
* еще какой-нибудь, если посчитаете нужным

## Теоретическая справка
### Backend
Простое приложение, которое демонстрирует стандартный микросервис с CRUD (Create, Read, Update, Delete операциями):
* Есть API (Applciation Programming Interface)
* Есть обращения к БД
* Есть сбор метрик
Для более подробной информации по коду, предлагаю закинуть его в LLM. Но он достаточно простой.

### Docker
Сборка образа backend-приложения происходит из Dockerfile. Dockerfile использует многостадийную (multistage) сборку для создания образа приложения на Go.

**Этапы**
1. Стадия сборки: берем базовый образ golang:1.21-alpine, копируем в него зависимости (go.mod, go.sum), загружаем зависимости, собираем приложение - на выходе бинарник.
2. Финальная стадия: берем базовый легковесный образ, копируем в него бинарник, запускаем его.

### Docker Compose
Развертывание всех компонентов происходит c помощью Docker Compose.

Используем open-source образы компонентов с docker hub:
* nginx:alpine 
* postgres:15
* prometheuscommunity/postgres-exporter:v0.15.0
* prom/node-exporter
* prom/prometheus:latest
* grafana/grafana:9.0.0
* gcr.io/cadvisor/cadvisor:latest

И кастомный образ нашего backend приложения: backend


### NGINX
Выступает у нас как веб сервер и как обратный прокси (reverse proxy).
В чем суть:
* Web Server: обслуживание статических файлов. Мы задаем сервер, который слушает на 80 порту. Задаем директорию с файлами и главную страницу. При обращении на NGINX он отдает эту "статику" - HTML с JavaScript из директории ui.
* Reverse Proxy: проксирует запросы на бэкенд (маршрутизация)


### Prometheus
В конфигурации мы описываем откуда "скрепим" (забираем / пуллим) метрики.