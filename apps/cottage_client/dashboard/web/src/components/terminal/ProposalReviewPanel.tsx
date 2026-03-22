import { Panel } from './Panel'
import type { MissionProposalItem } from './types'

type Props = {
  proposals: MissionProposalItem[]
  selectedProposalId?: string
  onSelect: (proposalId: string) => void
  onApprove: (proposalId: string) => void
  onDispatch: (proposalId: string) => void
}

export function ProposalReviewPanel({ proposals, selectedProposalId, onSelect, onApprove, onDispatch }: Props) {
  if (proposals.length === 0) return null

  const selected = proposals.find((proposal) => proposal.id === selectedProposalId) ?? proposals[0]

  return (
    <Panel title="Pending Approval" meta={`${proposals.length} awaiting review`}>
      <div className="proposal-list">
        {proposals.map((proposal) => (
          <button
            className={`proposal-row${proposal.id === selected.id ? ' is-selected' : ''}`}
            key={proposal.id}
            onClick={() => onSelect(proposal.id)}
          >
            <strong>{proposal.title}</strong>
            <span>{proposal.summary ?? 'Mission proposal ready for review.'}</span>
          </button>
        ))}
      </div>

      <div className="detail-stack">
        <div className="detail-row"><span>Approval</span><strong>{selected.approvalStatus.replace('_', ' ')}</strong></div>
        {selected.from || selected.to ? <div className="detail-row"><span>Route</span><strong>{`${selected.from ?? 'Site'} -> ${selected.to ?? 'Site'}`}</strong></div> : null}
        {selected.summary ? <div className="detail-row"><span>Summary</span><strong>{selected.summary}</strong></div> : null}
        {selected.replanSummary ? <div className="detail-row"><span>Replan</span><strong>{selected.replanSummary}</strong></div> : null}
      </div>

      {selected.steps.length ? (
        <div className="proposal-steps">
          {selected.steps.map((step) => (
            <div className="proposal-step" key={step.id}>
              <strong>{step.summary}</strong>
              <span>{step.topCandidate ? `Top candidate: ${step.topCandidate}` : 'No current candidate'}</span>
              {step.routeLabels?.length ? <span>{`Route: ${step.routeLabels.join(' -> ')}`}</span> : null}
            </div>
          ))}
        </div>
      ) : null}

      {selected.assumptions?.length ? (
        <div className="proposal-flags">
          {selected.assumptions.map((assumption) => <span key={assumption}>{assumption}</span>)}
        </div>
      ) : null}

      {selected.operatorNotes?.length ? (
        <div className="proposal-flags">
          {selected.operatorNotes.map((note) => <span key={note}>{note}</span>)}
        </div>
      ) : null}

      {selected.blockingReasons.length ? (
        <div className="proposal-flags proposal-flags--blocked">
          {selected.blockingReasons.map((reason) => <span key={reason}>{reason}</span>)}
        </div>
      ) : null}

      {selected.warnings.length ? (
        <div className="proposal-flags">
          {selected.warnings.map((warning) => <span key={warning}>{warning}</span>)}
        </div>
      ) : null}

      {selected.approvalStatus === 'approved' ? (
        <button className="action-button action-button--primary" onClick={() => onDispatch(selected.id)} disabled={!selected.executable}>
          Dispatch Mission
        </button>
      ) : (
        <button className="action-button action-button--primary" onClick={() => onApprove(selected.id)} disabled={!selected.executable}>
          Approve Mission
        </button>
      )}
    </Panel>
  )
}
