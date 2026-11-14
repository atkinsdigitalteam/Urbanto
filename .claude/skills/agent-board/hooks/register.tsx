import { atom, read, update } from 'claude-code'
import type {
  AgentInfo,
  AgentSpawnInput,
  Color,
  EngineInterface,
  Register,
  Timer,
  TurnCompleteReason,
} from 'claude-code'

import type { Role, Worker, WorkerStatus } from '../types'

// Agent board: a live side panel of every helper agent this session starts.
//
// It never calls a model, adds nothing to the system prompt and appends no
// rows to the conversation, so it costs no tokens. Everything it shows comes
// from events the engine raises anyway: an agent starting, each tool it uses,
// and its turn ending.

const PANE = 'agent-board'
const TITLE = 'Agent board'
const KEEP = 40
const BEAT_MS = 2000

const workers = atom({ plugin: 'agent-board', key: 'workers' } as const, [], {
  shape: 'workers-1',
})
const lead = atom({ plugin: 'agent-board', key: 'lead' } as const, '')
const tick = atom({ plugin: 'agent-board', key: 'tick' } as const, 0)
const isDismissed = atom(
  { plugin: 'agent-board', key: 'isDismissed' } as const,
  false,
)

type $ = EngineInterface

// ---------------------------------------------------------------- roles

const ROLE_BY_TYPE: Record<string, Role> = {
  'claude-code-guide': 'Researcher',
  'statusline-setup': 'Developer',
}

const RULES: ReadonlyArray<readonly [Role, RegExp]> = [
  [
    'Reviewer',
    /\b(review|audit|verif|critiqu|inspect|lint|security|qa\b|proofread)/i,
  ],
  ['Tester', /\b(tests?\b|testing|tester|e2e|coverage|regression)/i],
  [
    'Designer',
    /\b(design|ui\b|ux\b|layout|styl|css|theme|mock-?up|visual|figma|icon|colou?r|typograph|wireframe|brand|logo)/i,
  ],
  ['Planner', /\b(plan\b|plann|architect|strateg|roadmap|break ?down|scop)/i],
  [
    'Researcher',
    /\b(research|explor|search|find|investigat|look ?up|locat|survey|analy[sz]|understand|scan|discover|gather)/i,
  ],
  [
    'Writer',
    /\b(docs?\b|documentation|readme|copy ?writ|blog|article|content|summar|translat|changelog|release notes)/i,
  ],
  [
    'Developer',
    /\b(implement|build|fix|code\b|coding|refactor|develop|add\b|creat|migrat|debug|wire|integrat|updat|program|engineer|script|endpoint|api\b|bug)/i,
  ],
]

function matchRole(text: string): Role | undefined {
  for (const [role, rule] of RULES) {
    if (rule.test(text)) return role
  }

  return undefined
}

/** The agent type names the role best; then its task's few words; then its prompt. */
function roleOf(type: string, description: string, prompt: string): Role {
  return (
    ROLE_BY_TYPE[type] ??
    matchRole(type.replace(/[-_:]/g, ' ')) ??
    matchRole(description) ??
    matchRole(prompt.slice(0, 400)) ??
    'Assistant'
  )
}

const LOOK: Record<Role, { icon: string; color: Color }> = {
  Designer: { icon: '🎨', color: 'merged' },
  Developer: { icon: '💻', color: 'suggestion' },
  Reviewer: { icon: '🔍', color: 'warning' },
  Tester: { icon: '🧪', color: 'success' },
  Researcher: { icon: '📚', color: 'ide' },
  Planner: { icon: '🧭', color: 'planMode' },
  Writer: { icon: '📝', color: 'remember' },
  Assistant: { icon: '🤖', color: 'claude' },
}

// Tool calls an agent of each role usually makes before it is done: the pace
// of the estimate when the agent keeps no to-do list.
const PACE: Record<Role, number> = {
  Designer: 25,
  Developer: 30,
  Reviewer: 18,
  Tester: 25,
  Researcher: 20,
  Planner: 18,
  Writer: 15,
  Assistant: 25,
}

// ---------------------------------------------------------------- actions

function str(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

function clip(text: string, room = 80): string {
  const line = text.replace(/\s+/g, ' ').trim()

  return line.length > room ? `${line.slice(0, room - 1)}…` : line
}

function fileOf(path: string): string {
  const parts = path.split('/').filter(Boolean)

  return parts.slice(-2).join('/') || path
}

function hostOf(url: string): string {
  try {
    return new URL(url).host
  } catch {
    return clip(url, 40)
  }
}

function firstLine(text: string): string {
  return text.split('\n').find(line => line.trim() !== '') ?? ''
}

/** A tool call in plain words: what the agent is doing right now. */
function describeAction(tool: string, a: Record<string, unknown>): string {
  switch (tool) {
    case 'Read':
      return `Reading ${fileOf(str(a.file_path))}`
    case 'Write':
      return `Writing ${fileOf(str(a.file_path))}`
    case 'Edit':
      return `Editing ${fileOf(str(a.file_path))}`
    case 'NotebookEdit':
      return `Editing notebook ${fileOf(str(a.notebook_path))}`
    case 'Bash': {
      const said = str(a.description)

      return said !== '' ? clip(said) : `Running ${clip(str(a.command), 60)}`
    }
    case 'Grep':
      return `Searching the code for "${clip(str(a.pattern), 40)}"`
    case 'Glob':
      return `Looking for files: ${clip(str(a.pattern), 40)}`
    case 'WebFetch':
      return `Reading a web page (${hostOf(str(a.url))})`
    case 'WebSearch':
      return `Searching the web for "${clip(str(a.query), 40)}"`
    case 'Agent':
      return `Handing a job to a helper: ${clip(str(a.description), 50)}`
    case 'TodoWrite':
      return 'Updating its to-do list'
    case 'TaskCreate':
      return `Planning a step: ${clip(str(a.subject), 50)}`
    case 'TaskUpdate':
      return str(a.activeForm) !== ''
        ? clip(str(a.activeForm))
        : 'Updating its to-do list'
    case 'Skill':
      return `Using the ${str(a.skill)} skill`
    case 'ToolSearch':
      return 'Loading the tools it needs'
    case 'Artifact':
      return 'Publishing a page'
    case 'SendMessage':
      return 'Messaging another agent'
    case 'AskUserQuestion':
      return 'Waiting for your answer'
    case 'LSP':
      return 'Checking the code with the language server'
  }
  if (tool.startsWith('mcp__')) {
    const [, server = '', name = ''] = tool.split('__')

    return `Using ${server.replace(/[_-]+/g, ' ')}: ${name.replace(/[_-]+/g, ' ')}`
  }

  return `Using ${tool}`
}

// ---------------------------------------------------------------- workers

const ACTIVE: ReadonlySet<WorkerStatus> = new Set(['starting', 'working', 'thinking'])

function isActive(w: Worker): boolean {
  return ACTIVE.has(w.status)
}

function trim(list: Worker[]): Worker[] {
  const active = list.filter(isActive)
  const rest = list
    .filter(w => !isActive(w))
    .sort((a, b) => (b.endedAt ?? b.startedAt) - (a.endedAt ?? a.startedAt))
    .slice(0, Math.max(0, KEEP - active.length))
  const kept = new Set([...active, ...rest].map(w => w.id))

  return list.filter(w => kept.has(w.id))
}

function finish(w: Worker, reason: TurnCompleteReason, at: number): Worker {
  if (reason === 'answer' && w.isTeammate) {
    return { ...w, status: 'idle', now: 'Waiting for its next message', task: undefined }
  }
  const status: WorkerStatus =
    reason === 'answer' ? 'done' : reason === 'aborted' ? 'stopped' : 'failed'
  const now =
    status === 'done' ? 'Finished and reported back' : status === 'stopped' ? 'Stopped' : 'Ran into an error'

  return { ...w, status, now, task: undefined, endedAt: at }
}

function advance(w: Worker, tool: string, a: Record<string, unknown>, action: string): Worker {
  let next: Worker = {
    ...w,
    steps: w.steps + 1,
    status: isActive(w) ? 'thinking' : w.status,
    now: isActive(w) ? 'Thinking about the next step' : w.now,
    recent: [...w.recent, action].slice(-3),
  }
  if (tool === 'TodoWrite' && Array.isArray(a.todos)) {
    const todos = a.todos as ReadonlyArray<{ status?: string; activeForm?: string; content?: string }>
    const doing = todos.find(t => t.status === 'in_progress')
    next = {
      ...next,
      todoTotal: todos.length,
      todoDone: todos.filter(t => t.status === 'completed').length,
      task: doing ? clip(str(doing.activeForm) || str(doing.content), 70) : undefined,
    }
  } else if (tool === 'TaskCreate') {
    next = { ...next, todoTotal: next.todoTotal + 1 }
  } else if (tool === 'TaskUpdate') {
    if (a.status === 'completed') {
      next = { ...next, todoDone: Math.min(next.todoDone + 1, next.todoTotal) }
    } else if (a.status === 'deleted') {
      next = { ...next, todoTotal: Math.max(next.todoTotal - 1, next.todoDone) }
    } else if (a.status === 'in_progress' && str(a.activeForm) !== '') {
      next = { ...next, task: clip(str(a.activeForm), 70) }
    }
  }

  return next
}

function progressOf(w: Worker): { value: number; text: string } {
  if (w.status === 'done') return { value: 1, text: '100%' }
  const value =
    w.todoTotal > 0
      ? Math.min(w.todoDone / w.todoTotal, 0.97)
      : Math.min(0.95, 0.03 + 0.92 * (1 - Math.exp(-w.steps / PACE[w.role])))
  const percent = Math.round(value * 100)
  const figure =
    w.todoTotal > 0 ? `${percent}% · ${w.todoDone}/${w.todoTotal} steps` : `about ${percent}%`
  if (w.status === 'stopped') return { value, text: `stopped at ${figure}` }
  if (w.status === 'failed') return { value, text: `failed at ${figure}` }
  if (w.status === 'idle') return { value: 1, text: 'job done, waiting' }

  return { value, text: figure }
}

async function safely(work: Promise<unknown>): Promise<void> {
  try {
    await work
  } catch {
    // The board is a viewer: nothing it fails at may get in an agent's way.
  }
}

function patch($: $, id: string, fn: (w: Worker) => Worker): Promise<void> {
  return safely(update($, workers, list => list.map(w => (w.id === id ? fn(w) : w))))
}

async function openPane($: $): Promise<void> {
  if (await read($, isDismissed)) return
  await safely($.ui.open({ id: PANE, title: TITLE }))
}

// Loops the engine runs for itself (compaction, memory) carry agent ids that
// no list names: remember them so they are looked up once.
const ignored = new Set<string>()

function fromInfo(info: AgentInfo, at: number): Worker {
  return {
    id: info.id,
    title: clip(info.description || info.name || info.type, 60),
    type: info.type,
    role: roleOf(info.type, info.description, ''),
    status: 'working',
    now: 'Working',
    steps: 0,
    todoDone: 0,
    todoTotal: 0,
    startedAt: at,
    parentId: info.parentId,
    isTeammate: info.teammateId !== undefined,
    recent: [],
  }
}

async function isTracked($: $, id: string): Promise<boolean> {
  if (ignored.has(id)) return false
  if ((await read($, workers)).some(w => w.id === id)) return true
  const info = (await $.agent.list()).find(one => one.id === id)
  if (info === undefined) {
    ignored.add(id)

    return false
  }
  const at = await $.clock.now()
  await update($, workers, list =>
    list.some(w => w.id === id) ? list : trim([...list, fromInfo(info, at)]),
  )

  return true
}

async function recordSpawn($: $, e: AgentSpawnInput, id: string): Promise<void> {
  ignored.delete(id)
  const at = await $.clock.now()
  const title = clip(
    [e.description || firstLine(e.prompt) || e.subagentType, e.name ? `(${e.name})` : '']
      .filter(Boolean)
      .join(' '),
    60,
  )
  const fresh: Worker = {
    id,
    title,
    type: e.workflow ? `${e.subagentType} · workflow` : e.subagentType,
    role: roleOf(e.subagentType, e.description, e.prompt),
    status: 'starting',
    now: e.resume ? 'Picking up a new message' : 'Getting started',
    steps: 0,
    todoDone: 0,
    todoTotal: 0,
    startedAt: at,
    parentId: e.parentAgentId,
    isTeammate: e.isTeammate === true,
    recent: [],
  }
  await update($, workers, list => {
    const known = list.find(w => w.id === id)
    if (known === undefined) return trim([...list, fresh])
    if (e.resume) {
      return list.map(w =>
        w.id === id ? { ...w, status: 'starting', now: fresh.now, endedAt: undefined } : w,
      )
    }

    // Its first tool call got here before this spawn did: keep the progress,
    // take the spawn's better names.
    return list.map(w =>
      w.id === id ? { ...w, title, type: fresh.type, role: fresh.role, isTeammate: fresh.isTeammate } : w,
    )
  })
  await openPane($)
}

/** Every couple of seconds while agents work: catch ends no turn reported, tick the clocks. */
async function beat($: $): Promise<void> {
  const list = await read($, workers)
  if (!list.some(isActive)) return
  const ended = new Map<string, TurnCompleteReason>()
  for (const info of await $.agent.list()) {
    if (info.status === 'completed') ended.set(info.id, 'answer')
    if (info.status === 'killed') ended.set(info.id, 'aborted')
    if (info.status === 'failed') ended.set(info.id, 'error')
  }
  const at = await $.clock.now()
  if (list.some(w => isActive(w) && ended.has(w.id))) {
    await update($, workers, all =>
      all.map(w => {
        const reason = ended.get(w.id)

        return isActive(w) && reason !== undefined ? finish(w, reason, at) : w
      }),
    )
  }
  await update($, tick, n => n + 1)
}

// ---------------------------------------------------------------- drawing

function elapsed(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000))
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ${String(s % 60).padStart(2, '0')}s`

  return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m`
}

const STATUS_WORD: Record<WorkerStatus, string> = {
  starting: 'Starting',
  working: 'Working',
  thinking: 'Thinking',
  idle: 'Waiting',
  done: 'Done ✓',
  failed: 'Failed',
  stopped: 'Stopped',
}

function order(list: Worker[]): Worker[] {
  return [...list].sort((a, b) => {
    const rank = Number(isActive(b)) - Number(isActive(a))

    return rank !== 0 ? rank : a.startedAt - b.startedAt
  })
}

// ---------------------------------------------------------------- hooks

export const register: Register = on => {
  let beatTimer: Timer | undefined

  on('session.start', async ($, e, next) => {
    await safely(
      $.command.register({
        name: 'agent-board',
        description: 'Open the agent board: every helper agent, its role, progress and current step',
      }),
    )
    beatTimer?.cancel()
    try {
      beatTimer = $.clock.every(BEAT_MS, () => void safely(beat($)))
    } catch {
      beatTimer = undefined
    }
    void openPane($)

    return next(e)
  })

  on('command.run', { command: 'agent-board' }, async $ => {
    await update($, isDismissed, () => false)
    await $.ui.open({ id: PANE, title: TITLE })

    return {}
  })

  on('ui.close', async ($, e, next) => {
    if (e.id === PANE && e.origin.kind === 'person') {
      await safely(update($, isDismissed, () => true))
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('agent.spawn', async ($, e, next) => {
    const started = await next(e)
    if (started.agentId !== undefined) {
      await safely(recordSpawn($, e, started.agentId))
    }

    return started
  }).catch(($, e, next) => next(e))

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) await safely(update($, lead, () => 'Thinking'))

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const tool = String(e.tool)
    const args = e as unknown as Record<string, unknown>
    const action = describeAction(tool, args)
    const id = e.agentId

    if (id === undefined) {
      await safely(update($, lead, () => action))

      return next(e)
    }
    let tracked = false
    try {
      tracked = await isTracked($, id)
    } catch {
      tracked = false
    }
    if (!tracked) return next(e)

    await patch($, id, w => (isActive(w) ? { ...w, status: 'working', now: action } : w))
    const ran = await next(e)
    await patch($, id, w => advance(w, tool, args, action))

    return ran
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const id = e.agentId
    if (id === undefined) {
      await safely(update($, lead, () => 'Finished its reply, waiting for you'))

      return next(e)
    }
    const at = await $.clock.now()
    await patch($, id, w => finish(w, e.reason, at))

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Progress, Button } = $.ui.resolve(e)
    const list = order(await read($, workers))
    const leadNow = await read($, lead)
    await read($, tick)
    const now = await $.clock.now()

    const active = list.filter(isActive)
    const finished = list.length - active.length
    const titleOf = new Map(list.map(w => [w.id, w.title]))
    const summary =
      active.length === 0
        ? 'No agents working right now'
        : `${active.length} agent${active.length === 1 ? '' : 's'} working`
    const tail = finished > 0 ? ` · ${finished} finished` : ''

    if (e.props.placement === 'widget') {
      return (
        <Box flexDirection="column">
          <Text bold>{summary + tail}</Text>
          {active.slice(0, 4).map(w => {
            const p = progressOf(w)

            return (
              <Progress
                label={`${LOOK[w.role].icon} ${w.role}: ${w.title}`}
                value={p.value}
                valueText={p.text}
                color={LOOK[w.role].color}
              />
            )
          })}
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        <Box flexDirection="column" marginBottom={1}>
          <Text bold>{summary + tail}</Text>
          {leadNow !== '' && <Text dimColor wrap="truncate-end">{`Lead (Claude): ${leadNow}`}</Text>}
        </Box>

        {list.length === 0 && (
          <Text dimColor>
            When Claude hands work to helper agents, each one shows up here with its role, its progress and what it is doing right now.
          </Text>
        )}

        {list.map(w => {
          const look = LOOK[w.role]
          const p = progressOf(w)
          const clock = elapsed((w.endedAt ?? now) - w.startedAt)
          const parent = w.parentId !== undefined ? titleOf.get(w.parentId) : undefined
          const live = isActive(w)

          return (
            <Box
              key={`card-${w.id}`}
              flexDirection="column"
              borderStyle="round"
              borderColor={live ? look.color : 'subtle'}
              paddingX={1}
              marginBottom={1}
              marginLeft={w.parentId !== undefined ? 2 : 0}
            >
              <Box flexDirection="row" justifyContent="space-between">
                <Text bold color={look.color}>{`${look.icon} ${w.role}`}</Text>
                <Text dimColor>{`${STATUS_WORD[w.status]} · ${clock}`}</Text>
              </Box>
              <Text wrap="truncate-end">{w.title}</Text>
              <Text dimColor wrap="truncate-end">
                {parent !== undefined ? `${w.type} · helping "${parent}"` : w.type}
              </Text>
              <Progress label={w.title || w.role} value={p.value} valueText={p.text} color={look.color} />
              {w.task !== undefined && <Text wrap="wrap">{`Working on: ${w.task}`}</Text>}
              <Text wrap="wrap" dimColor={!live}>{`Now: ${w.now}`}</Text>
              {w.recent.length > 0 && (
                <Text dimColor wrap="truncate-end">{`Just did: ${[...w.recent].reverse().join(' · ')}`}</Text>
              )}
              {live && (
                <Button
                  key={`view-${w.id}`}
                  plain
                  label="Open its conversation"
                  onPress={async () => {
                    const shown = await $.ui.view({ agentId: w.id })
                    if (shown.deny !== undefined) $.ui.toast(`Can't open it: ${shown.deny}`)
                  }}
                />
              )}
            </Box>
          )
        })}

        {finished > 0 && (
          <Button
            key="clear-finished"
            label="Clear finished"
            onPress={() => update($, workers, all => all.filter(isActive))}
          />
        )}
      </Box>
    )
  })
}
