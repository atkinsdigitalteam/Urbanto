import type { AgentInfo } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

const PANE = {
  plugin: 'agent-board',
  component: 'Pane',
  requestId: 'agent-board',
  props: {
    title: 'Agent board',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 60 },
    view: {},
  },
} as const

test('a spawned agent shows its role, its step and its progress, on every surface', async ($, on) => {
  // Nothing sits beneath the plugin: each hook here stands for the engine.
  on('command.register', () => ({ value: { command: 'agent-board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('agent.spawn', () => ({ model: 'test-model', agentId: 'a1' }))
  let agents: AgentInfo[] = []
  on('agent.list', () => ({ value: agents }))
  on('tool.call', () => ({ result: {} }))
  const clock = mock.clock(on, { now: 1_000_000 })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.agent.spawn({
    tool_use_id: 'tu1',
    prompt: 'Make the landing page hero look modern.',
    description: 'Redesign hero layout',
    subagentType: 'general-purpose',
    provider: { plugin: 'engine', tier: 'core' },
    parentModel: 'test-model',
    background: true,
    fork: false,
  })
  await $.tool.call({
    tool: 'TodoWrite',
    agentId: 'a1',
    todos: [
      { content: 'Read hero', status: 'completed', activeForm: 'Reading hero' },
      { content: 'Restyle hero', status: 'in_progress', activeForm: 'Restyling the hero' },
      { content: 'Check on mobile', status: 'pending', activeForm: 'Checking on mobile' },
      { content: 'Report back', status: 'pending', activeForm: 'Reporting back' },
    ],
  })
  await $.tool.call({ tool: 'Read', file_path: '/repo/src/components/Hero.tsx', agentId: 'a1' })

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })

    expect((await ui.find({ type: 'Text', text: /agent working/ }))?.text).toBe('1 agent working')
    expect((await ui.find({ type: 'Text', text: /Designer/ }))?.text).toContain('Designer')
    expect((await ui.find({ type: 'Text', text: /^Working on:/ }))?.text).toBe(
      'Working on: Restyling the hero',
    )
    expect((await ui.find({ type: 'Text', text: /^Just did:/ }))?.text).toBe(
      'Just did: Reading components/Hero.tsx · Updating its to-do list',
    )
    // A surface may draw the bar its own way: find its figure, whatever holds it.
    expect(await ui.find({ text: /25% · 1\/4 steps/ })).toBeDefined()
    await ui.unmount()
  }

  // The agent ends: the board's next heartbeat (2s on) sees it in the agent
  // list, and its clock stops there however long the board stays open.
  agents = [{ id: 'a1', description: 'Redesign hero layout', type: 'general-purpose', status: 'completed' }]
  await clock.advance(65_000)
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /finished/ }))?.text).toBe('No agents working right now · 1 finished')
  expect((await ui.find({ type: 'Text', text: /Done/ }))?.text).toBe('Done ✓ · 2s')
  expect(await ui.find({ text: /^100%$/ })).toBeDefined()
  await ui.unmount()
})

test('with no agents the pane says so', async ($, on) => {
  on('ui.open', () => ({ value: { isPlaced: true } }))
  mock.clock(on)
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: /No agents/ }))?.text).toBe(
    'No agents working right now',
  )
  await ui.unmount()
})
