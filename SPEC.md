# Telegram Bot for Dating

## Overview
- **Bot name**: DatingBot
- **Type**: Telegram bot for dating/connections
- **Core functionality**: Anonimous chat for dating, пользователи ищут попутчиков/пару
- **Target users**: Люди, ищущие знакомства

## Tech Stack
- Python 3.x
- python-telegram-bot (aiogram 3.x)
- SQLite for data storage
- Docker for deployment

## Functionality

### Core Features

1. **User Registration**
   - Регистрация через команду /start
   - Анкета: имя, возраст, пол, описание, фото
   - Настройки поиска: кто ищет (мужчин/женщин/всех)

2. **Viewing Profiles**
   - Просмотр анкет с помощью кнопок "Далее" / "Нравится"
   - Если "Нравится" и другому человеку тоже - мэтч!

3. **Chat**
   - Анонимный чат между мэтчнувшимися пользователями
   - Возможность завершить чат

4. **Profile Management**
   - Редактирование анкеты
   - Просмотр своей анкеты
   - Удаление анкеты

### User Flow
1. User sends /start
2. Bot asks for registration (name, age, gender, about, photo)
3. User can browse profiles
4. If like → check if mutual → create chat

## Data Model

### User
- id (telegram user id)
- name
- age
- gender (male/female)
- looking_for (male/female/both)
- description
- photo_file_id
- is_active

### Match
- user1_id
- user2_id
- created_at

### Chat
- id
- user1_id
- user2_id
- created_at

## Commands
- /start - Регистрация
- /profile - Моя анкета
- /edit - Редактировать анкету
- /search - Искать анкеты
- /stop - Удалить анкету
- /help - Помощь

## API

- None (Telegram Bot API only)

## Configuration (config.py)
- BOT_TOKEN
- ADMIN_IDS

## Acceptance Criteria
1. User can register with photo
2. User can browse profiles
3. Mutual likes create a chat
4. Users can chat anonymously
5. Bot responds within 3 seconds