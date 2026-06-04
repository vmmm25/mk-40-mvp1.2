from .email_read_tool import EmailReadTool
from .email_send_tool import EmailSendTool
from .search_documents_tool import SearchDocumentsTool
from .index_document_tool import IndexDocumentTool
from .open_app_tool import OpenAppTool
from .web_search_tool import WebSearchTool
from .weather_report_tool import WeatherReportTool
from .send_message_tool import SendMessageTool
from .reminder_tool import ReminderTool
from .youtube_video_tool import YoutubeVideoTool
from .screen_process_tool import ScreenProcessTool
from .computer_settings_tool import ComputerSettingsTool
from .browser_control_tool import BrowserControlTool
from .file_controller_tool import FileControllerTool
from .desktop_control_tool import DesktopControlTool
from .code_helper_tool import CodeHelperTool
from .dev_agent_tool import DevAgentTool
from .agent_task_tool import AgentTaskTool
from .computer_control_tool import ComputerControlTool
from .game_updater_tool import GameUpdaterTool
from .flight_finder_tool import FlightFinderTool
from .smart_home_tool import SmartHomeTool
from .git_operation_tool import GitOperationTool
from .docker_control_tool import DockerControlTool
from .database_query_tool import DatabaseQueryTool
from .play_music_tool import PlayMusicTool
from .generate_image_tool import GenerateImageTool
from .calendar_list_events_tool import CalendarListEventsTool
from .calendar_create_event_tool import CalendarCreateEventTool
from .shutdown_jarvis_tool import ShutdownJarvisTool
from .file_processor_tool import FileProcessorTool
from .save_memory_tool import SaveMemoryTool
from .process_with_openrouter_tool import ProcessWithOpenrouterTool
from .terminal_control_tool import TerminalControlTool

ALL_TOOLS = [
    EmailReadTool(),
    EmailSendTool(),
    SearchDocumentsTool(),
    IndexDocumentTool(),
    OpenAppTool(),
    WebSearchTool(),
    WeatherReportTool(),
    SendMessageTool(),
    ReminderTool(),
    YoutubeVideoTool(),
    ScreenProcessTool(),
    ComputerSettingsTool(),
    BrowserControlTool(),
    FileControllerTool(),
    DesktopControlTool(),
    CodeHelperTool(),
    DevAgentTool(),
    AgentTaskTool(),
    ComputerControlTool(),
    GameUpdaterTool(),
    FlightFinderTool(),
    SmartHomeTool(),
    GitOperationTool(),
    DockerControlTool(),
    DatabaseQueryTool(),
    PlayMusicTool(),
    GenerateImageTool(),
    CalendarListEventsTool(),
    CalendarCreateEventTool(),
    ShutdownJarvisTool(),
    FileProcessorTool(),
    SaveMemoryTool(),
    ProcessWithOpenrouterTool(),
    TerminalControlTool(),
]
