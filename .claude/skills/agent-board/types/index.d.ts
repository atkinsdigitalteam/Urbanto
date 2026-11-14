export type Role =
  | 'Designer'
  | 'Developer'
  | 'Reviewer'
  | 'Tester'
  | 'Researcher'
  | 'Planner'
  | 'Writer'
  | 'Assistant'

export type WorkerStatus =
  | 'starting'
  | 'working'
  | 'thinking'
  | 'idle'
  | 'done'
  | 'failed'
  | 'stopped'

export type Worker = {
  id: string
  title: string
  type: string
  role: Role
  status: WorkerStatus
  now: string
  task?: string
  steps: number
  todoDone: number
  todoTotal: number
  startedAt: number
  endedAt?: number
  parentId?: string
  isTeammate: boolean
  recent: string[]
}

declare module 'claude-code' {
  interface PluginState {
    'agent-board': {
      workers: Shaped<Worker[]>
      lead: string
      tick: number
      isDismissed: boolean
    }
  }
}
