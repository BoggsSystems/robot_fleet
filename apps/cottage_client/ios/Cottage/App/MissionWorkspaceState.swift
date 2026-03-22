import Foundation

enum MissionWorkspaceState {
    case compose
    case clarification(MissionPreviewResponse)
    case preview(MissionPreviewResponse)
    case detail(missionID: String)
}
