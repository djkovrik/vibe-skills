Мы пришли к двухэтапной схеме: сначала обычный Codex помогает вам сформировать спецификацию, затем в отдельной сессии $vibe-developer реализует её. Самому вручную заполнять десятки полей не предполагается. 
  
### Формат спецификации  
  
После создания skills появится шаблон Vibe AppSpec v1:  
  
app-spec/  
 app-spec.json # метаданные, requirements, capabilities и связи  
 product.md # аудитория, цели, non-goals, user stories  
 design.md # Lazyweb evidence, темы, типографика, иконки, previews/goldens
 domain.md # сущности, бизнес-правила, ошибки, время  
 data.md # API, БД, settings, offline и sync  
 quality.md # тесты, accessibility, privacy, release criteria  
 flows/  
 FLOW-*.md # пошаговые пользовательские сценарии  
 screens/  
 SCREEN-*.md # состояния и поведение каждого экрана  
 assets/  
  
JSON нужен для машинной проверки, Markdown — чтобы требования было удобно обсуждать и редактировать. Requirements, экраны, флоу и acceptance-сценарии получают стабильные идентификаторы вроде REQ-001, SCREEN-001, AC-001
  
### Рекомендуемый пользовательский процесс  
  
В первой сессии вы говорите обычному Codex примерно следующее:  
  
> Помоги спроектировать приложение. Проведи со мной продуктовое интервью: выясни цели, аудиторию, функции, ограничения, все экраны и UI/UX-флоу. До реализации составь инвентарь интерактивных элементов и реши, где нужны icon, text, icon+text или осознанно не нужна иконка. Попроси меня утвердить стандартный набор иконок или предоставить необходимые custom/brand assets; нерешённые материальные вопросы запиши как blocking openQuestions. Для локальных каталогов, базы/seed/reference data и другого встроенного текста зафиксируй стабильные IDs/общие localization keys: переводы хранятся только в Compose Multiplatform Resources locale-specific strings.xml, английский всегда является default/base locale, русский — начальной дополнительной локалью, а последующие локали легко добавляются с теми же ключами; resolved translations не попадают в domain/persistence/code. Язык приложения определяется только языком системы: не проектируй language picker, locale preference или app-specific locale override. Если Compose Resources недоступны в native actual, используй Android/iOS localization resources с английским default и без hardcoded copy. Для каждого основного экрана зафиксируй состояния, light/dark previews, нужные font-scale/locale stress cases, Paparazzi + ComposablePreviewScanner и обязательный Lazyweb review после golden screenshots. Код пока не пиши. После согласования создай Vibe AppSpec v1.2 по шаблону из \Sources\vibe-skills\vibe-developer\assets\app-spec-template и сохрани в D:\Projects\MyApp\app-spec.
  
Агент задаёт вопросы, формирует спецификацию и оставляет неразрешённые моменты в `openQuestions`. Вопросы об обязательных пользовательских иконках/ассетах помечаются `blocking: true`; валидатор не позволит начать реализацию, пока они не будут решены или явно waived. Вы просматриваете результат и просите исправлять его, пока всё не станет однозначным.
  
Затем запускается проверка:  
  
python D:\Sources\vibe-skills\vibe-developer\scripts\validate-app-spec.py D:\Projects\MyApp\app-spec 
  
В отдельной реализации-сессии:  
  
> Используй $vibe-developer. Реализуй приложение по спецификации D:\Projects\MyApp\app-spec. Сначала проверь спецификацию и покажи план. Не меняй утверждённые требования молча. 
  
### Вариант со Spec Kit  
  
Для сложных приложений можно сначала использовать GitHub Spec Kit:  
  
constitution  
→ specify  
→ clarify  
→ plan  
→ checklist  
→ tasks  
→ analyze  
→ преобразование в Vibe AppSpec  
→ реализация через $vibe-developer  
  
Но Spec Kit остаётся необязательным. Skills принимают стабильный Vibe AppSpec, независимо от того, создали вы его через Spec Kit, OpenSpec или обычное обсуждение с Codex. 
  
Главное решение: генерация спеки и реализация разведены по разным сессиям. $vibe-developer валидирует и исполняет утверждённую спецификацию, но не начинает заново придумывать продукт по ходу написания кода.
