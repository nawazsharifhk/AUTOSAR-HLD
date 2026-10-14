import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLE_DIR = "./data/sample_hld"
Path(SAMPLE_DIR).mkdir(parents=True, exist_ok=True)


def build_hld_v1(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []

    # Title & Metadata
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor("#0f172a"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor("#0369a1"))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("<b>AUTOSAR High-Level Design (HLD) Document</b>", title_style))
    story.append(Paragraph("<b>Subsystem:</b> Braking & Longitudinal Vehicle Dynamics Control | <b>Version:</b> 1.0", h2_style))
    story.append(Paragraph("<b>Document ID:</b> HLD-AUTOSAR-BRAKE-2026-V1.0 | <b>Classification:</b> Automotive Confidential", body_style))
    story.append(Spacer(1, 15))

    # Page 1: 1. Executive Summary & Scope
    story.append(Paragraph("<b>1.0 System Architecture Overview & Scope</b>", h2_style))
    story.append(Paragraph(
        "This High-Level Design (HLD) specifies the software architecture for the Next-Gen Braking and Longitudinal Vehicle Control system compliant with AUTOSAR Classic Release 4.4 and ISO 26262 ASIL-D functional safety standards. "
        "The architecture decomposes vehicle dynamics into specialized Software Components (SWCs) interacting via the AUTOSAR Runtime Environment (RTE).",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.1 Core Software Components Definition</b>", h2_style))
    story.append(Paragraph(
        "The subsystem comprises the following key Software Components (SWCs):<br/>"
        "• <b>BrakeController</b>: Application SWC (ASIL-D). Responsible for computing deceleration requests, hydraulic pressure modulation, and wheel slip regulation.<br/>"
        "• <b>VehicleController</b>: Application SWC (ASIL-D). High-level vehicle supervisor coordinating propulsion, braking balance, and vehicle stability state.<br/>"
        "• <b>SensorFusion</b>: Application SWC (ASIL-B). Consolidates perception telemetry from radar and wheel speed sensors into track estimates.<br/>"
        "• <b>RadarInterface</b>: Sensor SWC (ASIL-B). Interfaces with front long-range radar hardware over CAN-FD.<br/>"
        "• <b>SafetyController</b>: Complex SWC (ASIL-D). Independent watchdog and safe-state supervisor monitoring critical RTE signals.<br/>"
        "• <b>CAN_Gateway</b>: BSW Module (QM). Manages cyclic CAN-FD frame communication with external ECUs.",
        body_style
    ))
    story.append(Spacer(1, 15))

    # Page Break -> Page 2
    story.append(PageBreak())
    story.append(Paragraph("<b>2.0 Software Component Port Specifications</b>", h2_style))
    story.append(Paragraph(
        "Each AUTOSAR Software Component exposes defined R-Ports (Required) and P-Ports (Provided) connected via RTE virtual functional buses.",
        body_style
    ))
    story.append(Spacer(1, 10))

    comp_table = [
        ["Component (SWC)", "Type", "ASIL", "Provided Ports (P-Port)", "Required Ports (R-Port)"],
        ["BrakeController", "Application SWC", "ASIL-D", "P_BrakeCommand, P_BrakeStatus", "R_VehState, R_SensorFusionTrack"],
        ["VehicleController", "Application SWC", "ASIL-D", "P_VehState, P_TargetTorque", "R_DriverDemand, R_BrakeStatus"],
        ["SensorFusion", "Application SWC", "ASIL-B", "P_FusionTrack, P_ObstacleDist", "R_RadarRaw, R_WheelSpeed"],
        ["RadarInterface", "Sensor SWC", "ASIL-B", "P_RadarRaw", "R_CAN_RxMsg"],
        ["SafetyController", "Complex SWC", "ASIL-D", "P_SafeStateCmd", "R_BrakeCommand, R_VehState"],
        ["CAN_Gateway", "BSW Module", "QM", "P_CAN_RxMsg", "R_CAN_TxMsg"]
    ]
    t1 = Table(comp_table, colWidths=[110, 85, 55, 130, 130])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    # Page 2: Section 3.0
    story.append(Paragraph("<b>3.0 Interfaces and Signal Routing</b>", h2_style))
    story.append(Paragraph(
        "The following Sender-Receiver and Client-Server interfaces are defined across SWC boundaries:<br/>"
        "• <b>BrakeCommandInterface</b>: Source <b>BrakeController</b> -> Target <b>VehicleController</b>. Signals: TargetDeceleration (float32, m/s2), BrakePedalStatus (uint8), EBD_Active (boolean).<br/>"
        "• <b>SensorTelemetryInterface</b>: Source <b>SensorFusion</b> -> Target <b>BrakeController</b>. Signals: ObstacleDistance (float32, m), RelativeVelocity (float32, m/s), TimeToCollision (float32, s).<br/>"
        "• <b>RadarStreamInterface</b>: Source <b>RadarInterface</b> -> Target <b>SensorFusion</b>. Signals: RawTargetList (array of 16 targets), RadarStatus (uint8).<br/>"
        "• <b>SafetySupervisionInterface</b>: Source <b>SafetyController</b> -> Target <b>BrakeController</b>. Signals: SafeStateActive (boolean), OverrideBrakeLevel (uint8).<br/>"
        "• <b>VehicleTelemetryInterface</b>: Source <b>CAN_Gateway</b> -> Target <b>RadarInterface</b>. Signals: CAN_BusFrameData.",
        body_style
    ))

    # Page Break -> Page 3
    story.append(PageBreak())
    story.append(Paragraph("<b>4.0 Functional Safety & ASIL Decomposition (ISO 26262)</b>", h2_style))
    story.append(Paragraph(
        "Safety Goal SG-01: 'Prevent unintended deceleration or total loss of braking' is classified as ASIL-D. "
        "The BrakeController and SafetyController SWCs are allocated ASIL-D development lifecycle rigor. "
        "SensorFusion is assigned ASIL-B because environmental perception is validated against redundant driver override checks. "
        "CAN_Gateway operates at Quality Management (QM) with end-to-end (E2E) protection profiles implemented at the RTE level.",
        body_style
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>5.0 Execution Timing & Runnable Entities</b>", h2_style))
    story.append(Paragraph(
        "• <b>BrakeController_Step (10ms Periodic)</b>: Executes anti-lock and deceleration PID algorithms.<br/>"
        "• <b>VehicleController_Step (20ms Periodic)</b>: Coordinates powertrain and chassis arbitration.<br/>"
        "• <b>SensorFusion_Step (20ms Periodic)</b>: Merges radar object tracks.<br/>"
        "• <b>SafetyController_Watchdog (5ms Periodic)</b>: High-priority monitoring runnable.",
        body_style
    ))

    doc.build(story)
    print(f"Generated sample HLD v1.0 at: {output_path}")


def build_hld_v2(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor("#0f172a"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor("#0284c7"))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("<b>AUTOSAR High-Level Design (HLD) Document</b>", title_style))
    story.append(Paragraph("<b>Subsystem:</b> Braking, ADAS & Automated Lateral Control | <b>Version:</b> 2.0", h2_style))
    story.append(Paragraph("<b>Document ID:</b> HLD-AUTOSAR-BRAKE-2026-V2.0 | <b>Classification:</b> Automotive Confidential (Revision 2.0)", body_style))
    story.append(Spacer(1, 15))

    # Page 1: 1. Executive Summary & Scope
    story.append(Paragraph("<b>1.0 System Architecture Overview & Scope (Revision 2.0)</b>", h2_style))
    story.append(Paragraph(
        "This revised High-Level Design (HLD v2.0) incorporates Autonomous Driving Assistance (ADAS Level 2+) features, "
        "upgrading the braking and longitudinal dynamics pipeline to support Adaptive Cruise Control (ACC) and Automated Emergency Steering (AES). "
        "Legacy CAN-FD gateway architecture is replaced with a high-throughput Automotive Ethernet Backbone.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.1 Updated Software Components Definition</b>", h2_style))
    story.append(Paragraph(
        "• <b>BrakeController</b>: Application SWC (ASIL-D). Enhanced with regenerative brake blending and autonomous emergency braking (AEB) trigger.<br/>"
        "• <b>VehicleController</b>: Application SWC (ASIL-D). Central motion supervisor with multi-actuator torque vectoring.<br/>"
        "• <b>SensorFusion</b>: Application SWC (ASIL-D - <i>Upgraded from ASIL-B</i>). Tri-modal perception merging radar, vision, and ultrasonic tracks.<br/>"
        "• <b>RadarInterface</b>: Sensor SWC (ASIL-B). Upgraded for 77GHz imaging radar.<br/>"
        "• <b>CameraInterface</b>: [NEW] Sensor SWC (ASIL-B). Vision object classification and lane marker detection.<br/>"
        "• <b>ADASCruiseControl</b>: [NEW] Application SWC (ASIL-C). Calculates velocity profiles, gap regulation, and headway time.<br/>"
        "• <b>SafetyController</b>: Complex SWC (ASIL-D). Enhanced multi-core safe lockstep monitor.<br/>"
        "• <i>(Note: Legacy CAN_Gateway component removed in v2.0 in favor of EthernetSwitchSWC).</i>",
        body_style
    ))
    story.append(Spacer(1, 15))

    # Page Break -> Page 2
    story.append(PageBreak())
    story.append(Paragraph("<b>2.0 Revised Software Component Port Specifications</b>", h2_style))
    story.append(Spacer(1, 10))

    comp_table_v2 = [
        ["Component (SWC)", "Type", "ASIL", "Provided Ports (P-Port)", "Required Ports (R-Port)"],
        ["BrakeController", "Application SWC", "ASIL-D", "P_BrakeCommand, P_BrakeStatus, P_AEB_State", "R_VehState, R_ADAS_DecelReq"],
        ["VehicleController", "Application SWC", "ASIL-D", "P_VehState, P_TargetTorque", "R_DriverDemand, R_BrakeStatus, R_ADAS_MotionReq"],
        ["SensorFusion", "Application SWC", "ASIL-D", "P_FusionTrack, P_ObstacleDist, P_LaneGeometry", "R_RadarRaw, R_CameraVisionRaw"],
        ["RadarInterface", "Sensor SWC", "ASIL-B", "P_RadarRaw", "R_EthData_Radar"],
        ["CameraInterface", "Sensor SWC", "ASIL-B", "P_CameraVisionRaw", "R_EthData_Camera"],
        ["ADASCruiseControl", "Application SWC", "ASIL-C", "P_ADAS_DecelReq, P_ADAS_MotionReq", "R_FusionTrack, R_VehState"],
        ["SafetyController", "Complex SWC", "ASIL-D", "P_SafeStateCmd", "R_BrakeCommand, R_VehState, R_ADAS_DecelReq"]
    ]
    t2 = Table(comp_table_v2, colWidths=[110, 85, 55, 130, 130])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0369a1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('BOTTOMPADDING' , (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Page 2: Section 3.0
    story.append(Paragraph("<b>3.0 Updated Interfaces & Signal Routing</b>", h2_style))
    story.append(Paragraph(
        "• <b>ADAS_DecelRequestInterface</b>: [NEW] Source <b>ADASCruiseControl</b> -> Target <b>BrakeController</b>. Signals: TargetDecelerationReq (float32), UrgencyLevel (uint8), AEB_Arm (boolean).<br/>"
        "• <b>BrakeCommandInterface</b>: Source <b>BrakeController</b> -> Target <b>VehicleController</b>. Signals: TargetDeceleration (float32), BrakePedalStatus (uint8), EBD_Active (boolean), RegBrakeTorque (float32).<br/>"
        "• <b>CameraVisionStreamInterface</b>: [NEW] Source <b>CameraInterface</b> -> Target <b>SensorFusion</b>. Signals: ObjectBoundingBoxes, LaneCurvature, PedestrianDetectionFlag.<br/>"
        "• <b>SensorTelemetryInterface</b>: Source <b>SensorFusion</b> -> Target <b>ADASCruiseControl</b>. Signals: LeadVehicleDist, LeadVehicleSpeed, TargetCutInProb.<br/>"
        "• <b>SafetySupervisionInterface</b>: Source <b>SafetyController</b> -> Target <b>BrakeController</b>. Signals: SafeStateActive (boolean), OverrideBrakeLevel (uint8).",
        body_style
    ))

    # Page Break -> Page 3
    story.append(PageBreak())
    story.append(Paragraph("<b>4.0 Potential Inconsistency & Safety Notes (For Review)</b>", h2_style))
    story.append(Paragraph(
        "Architecture Observation: On Page 2, ADASCruiseControl is designated ASIL-C while its output connects directly to BrakeController (ASIL-D) via ADAS_DecelRequestInterface. "
        "Furthermore, in Section 3.0, ADASCruiseControl interfaces with BrakeController, but legacy reference on Page 3 still suggests direct override to SafetyController. "
        "This requires formal Human Engineer Review and Safety Manager signoff.",
        body_style
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>5.0 Execution Schedule & Ethernet Latency Budgets</b>", h2_style))
    story.append(Paragraph(
        "• <b>CameraInterface_Step (30ms Periodic)</b>: Processes vision frame inference metadata.<br/>"
        "• <b>ADASCruiseControl_Step (10ms Periodic)</b>: Headway distance control loop.<br/>"
        "• <b>BrakeController_Step (10ms Periodic)</b>: Closed-loop deceleration actuation.",
        body_style
    ))

    doc.build(story)
    print(f"Generated sample HLD v2.0 at: {output_path}")


def build_hld_v3(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor("#0f172a"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor("#10b981"))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("<b>AUTOSAR High-Level Design (HLD) Document</b>", title_style))
    story.append(Paragraph("<b>Subsystem:</b> Integrated Vehicle Motion Control & V2X Communication | <b>Version:</b> 3.0", h2_style))
    story.append(Paragraph("<b>Document ID:</b> HLD-AUTOSAR-BRAKE-2026-V3.0 | <b>Classification:</b> Automotive Confidential (Revision 3.0)", body_style))
    story.append(Spacer(1, 15))

    # Page 1: 1. Executive Summary & Scope
    story.append(Paragraph("<b>1.0 System Architecture Overview & Scope (Revision 3.0)</b>", h2_style))
    story.append(Paragraph(
        "This advanced High-Level Design (HLD v3.0) builds upon previous versions by integrating Vehicle-to-Everything (V2X) communication, "
        "Artificial Intelligence/Machine Learning (AI/ML) based decision making, and enhanced cybersecurity measures. "
        "The architecture now supports cooperative adaptive cruise control (CACC), platooning, and over-the-air (OTA) update capabilities.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.1 Updated Software Components Definition</b>", h2_style))
    story.append(Paragraph(
        "• <b>BrakeController</b>: Application SWC (ASIL-D). Now includes predictive braking based on V2X inputs and AI-driven road condition analysis.<br/>"
        "• <b>VehicleController</b>: Application SWC (ASIL-D). Expanded to manage V2X communication, AI/ML model inference, and cooperative vehicle control.<br/>"
        "• <b>SensorFusion</b>: Application SWC (ASIL-D). Now incorporates V2X perception data and AI-based object classification with confidence scoring.<br/>"
        "• <b>RadarInterface</b>: Sensor SWC (ASIL-B). Enhanced with AI-based target tracking and micro-Doppler signature analysis.<br/>"
        "• <b>CameraInterface</b>: Sensor SWC (ASIL-B). Now includes neural network inference for semantic segmentation and 3D object detection.<br/>"
        "• <b>ADASCruiseControl</b>: Application SWC (ASIL-C). Enhanced with cooperative adaptive cruise control (CACC) and platooning capabilities.<br/>"
        "• <b>AIDecisionMaker</b>: [NEW] Application SWC (ASIL-D). Processes sensor and V2X data using deep learning models for trajectory planning and risk assessment.<br/>"
        "• <b>V2XCommunicationManager</b>: [NEW] Communication SWC (ASIL-B). Handles DSRC/C-V2X messaging, security credentials, and message validation.<br/>"
        "• <b>CybersecurityManager</b>: [NEW] Complex SWC (ASIL-D). Implements intrusion detection, secure boot, and runtime application self-protection (RASP).<br/>"
        "• <b>OTAUpdateManager</b>: [NEW] Application SWC (ASIL-B). Manages secure over-the-air software updates and version control.<br/>"
        "• <b>SafetyController</b>: Complex SWC (ASIL-D). Now includes runtime monitoring of AI/ML models for functional safety compliance.<br/>"
        "• <i>(Note: Legacy CAN_Gateway component removed in favor of unified Ethernet/V2X communication stack.)</i>",
        body_style
    ))
    story.append(Spacer(1, 15))

    # Page Break -> Page 2
    story.append(PageBreak())
    story.append(Paragraph("<b>2.0 Updated Software Component Port Specifications</b>", h2_style))
    story.append(Spacer(1, 10))

    comp_table_v3 = [
        ["Component (SWC)", "Type", "ASIL", "Provided Ports (P-Port)", "Required Ports (R-Port)"],
        ["BrakeController", "Application SWC", "ASIL-D", "P_BrakeCommand, P_BrakeStatus, P_AEB_State, P_PredictiveBrakeReq", "R_VehState, R_ADAS_DecelReq, R_V2X_HazardAlert, R_AI_RiskAssessment"],
        ["VehicleController", "Application SWC", "ASIL-D", "P_VehState, P_TargetTorque, P_V2X_Status, P_AI_Planning", "R_DriverDemand, R_BrakeStatus, R_ADAS_MotionReq, R_SensorFusion_V2X"],
        ["SensorFusion", "Application SWC", "ASIL-D", "P_FusionTrack, P_ObstacleDist, P_LaneGeometry, P_V2X_Perception", "R_RadarRaw, R_CameraVisionRaw, R_V2X_RemotePerception"],
        ["RadarInterface", "Sensor SWC", "ASIL-B", "P_RadarRaw", "R_EthData_Radar, R_V2X_RadarConfig"],
        ["CameraInterface", "Sensor SWC", "ASIL-B", "P_CameraVisionRaw", "R_EthData_Camera, R_V2X_CameraConfig"],
        ["ADASCruiseControl", "Application SWC", "ASIL-C", "P_ADAS_DecelReq, P_ADAS_MotionReq, P_CACC_Command", "R_FusionTrack, R_VehState, R_V2X_PlatoonStatus"],
        ["AIDecisionMaker", "Application SWC", "ASIL-D", "P_AI_RiskAssessment, P_AI_Planning, P_AI_Trajectory", "R_SensorFusion_AI, R_V2X_AI_Input, R_SafetyMonitor_Feedback"],
        ["V2XCommunicationManager", "Communication SWC", "ASIL-B", "P_V2X_MessageTx, P_V2X_Status, P_V2X_SecurityEvent", "R_V2X_MessageRx, R_V2X_ConfigUpdate, R_CyberSecurity_Alert"],
        ["CybersecurityManager", "Complex SWC", "ASIL-D", "P_SecurityAlert, P_SecureBootStatus, P_RASP_Notification", "R_V2X_SecurityInput, R_OTA_Verification, R_SystemHealth"],
        ["OTAUpdateManager", "Application SWC", "ASIL-B", "P_UpdateStatus, P_VerificationResult", "R_UpdateRequest, R_VerificationChallenge, R_CyberSecurity_Approval"],
        ["SafetyController", "Complex SWC", "ASIL-D", "P_SafeStateCmd, P_AI_ModelStatus", "R_BrakeCommand, R_VehState, R_ADAS_DecelReq, R_AI_ModelOutput"]
    ]
    t3 = Table(comp_table_v3, colWidths=[110, 85, 55, 130, 130])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#047857")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 15))

    # Page Break -> Page 3
    story.append(PageBreak())
    story.append(Paragraph("<b>3.0 Updated Interfaces & Signal Routing</b>", h2_style))
    story.append(Paragraph(
        "• <b>ADAS_DecelRequestInterface</b>: Source <b>ADASCruiseControl</b> -> Target <b>BrakeController</b>. Signals: TargetDecelerationReq (float32), UrgencyLevel (uint8), AEB_Arm (boolean).<br/>"
        "• <b>BrakeCommandInterface</b>: Source <b>BrakeController</b> -> Target <b>VehicleController</b>. Signals: TargetDeceleration (float32), BrakePedalStatus (uint8), EBD_Active (boolean), RegBrakeTorque (float32).<br/>"
        "• <b>CameraVisionStreamInterface</b>: Source <b>CameraInterface</b> -> Target <b>SensorFusion</b>. Signals: ObjectBoundingBoxes, LaneCurvature, PedestrianDetectionFlag.<br/>"
        "• <b>SensorTelemetryInterface</b>: Source <b>SensorFusion</b> -> Target <b>ADASCruiseControl</b>. Signals: LeadVehicleDist, LeadVehicleSpeed, TargetCutInProb.<br/>"
        "• <b>V2X_HazardAlertInterface</b>: [NEW] Source <b>V2XCommunicationManager</b> -> Target <b>BrakeController</b>. Signals: HazardType (enum), Distance (float32), TimeToCollision (float32), Reliability (uint8).<br/>"
        "• <b>AI_RiskAssessmentInterface</b>: [NEW] Source <b>AIDecisionMaker</b> -> Target <b>BrakeController</b>. Signals: RiskLevel (float32), RecommendedAction (enum), Confidence (float32).<br/>"
        "• <b>AI_PlanningInterface</b>: [NEW] Source <b>AIDecisionMaker</b> -> Target <b>VehicleController</b>. Signals: TrajectoryPoints (array), VelocityProfile (array), SafetyMargin (float32).<br/>"
        "• <b>V2X_PlatoonStatusInterface</b>: [NEW] Source <b>V2XCommunicationManager</b> -> Target <b>ADASCruiseControl</b>. Signals: PlatoonID (uint16), PositionInPlatoon (uint8), SpacingDistance (float32).<br/>"
        "• <b>CyberSecurityAlertInterface</b>: [NEW] Source <b>CybersecurityManager</b> -> Target <b>SafetyController</b>. Signals: ThreatLevel (enum), AffectedComponent (string), RecommendedAction (enum).<br/>"
        "• <b>AI_ModelMonitorInterface</b>: [NEW] Source <b>SafetyController</b> -> Target <b>AIDecisionMaker</b>. Signals: ModelHealthStatus (enum), DeviationMetrics (struct), ResetRequired (boolean).",
        body_style
    ))

    # Page Break -> Page 4
    story.append(PageBreak())
    story.append(Paragraph("<b>4.0 Functional Safety & Security Considerations (ISO 26262 & ISO/SAE 21434)</b>", h2_style))
    story.append(Paragraph(
        "Safety Goal SG-01: 'Prevent unintended deceleration or total loss of braking' remains ASIL-D. "
        "Additional safety goals include SG-02: 'Prevent unsafe AI/ML behavior' (ASIL-D) and SG-03: 'Maintain secure vehicle communication' (ASIL-B). "
        "The BrakeController, VehicleController, AIDecisionMaker, and SafetyController SWCs are allocated ASIL-D development lifecycle rigor. "
        "SensorFusion is assigned ASIL-D due to its critical role in AI/ML perception pipeline. "
        "V2XCommunicationManager and CybersecurityManager address ISO/SAE 21434 cybersecurity requirements with ASIL-B and ASIL-D respectively.",
        body_style
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>5.0 Execution Schedule & Communication Latency Budgets</b>", h2_style))
    story.append(Paragraph(
        "• <b>CameraInterface_Step (30ms Periodic)</b>: Processes vision frame and runs neural network inference.<br/>"
        "• <b>RadarInterface_Step (20ms Periodic)</b>: Processes radar data with CFAR detection and AI-based tracking.<br/>"
        "• <b>SensorFusion_Step (20ms Periodic)</b>: Multi-modal fusion including V2X perception data.<br/>"
        "• <b>AIDecisionMaker_Step (50ms Periodic)</b>: Runs deep learning models for risk assessment and trajectory planning.<br/>"
        "• <b>V2XCommunicationManager_Step (100ms Periodic)</b>: Handles message transmission, reception, and security processing.<br/>"
        "• <b>CybersecurityManager_Step (500ms Periodic)</b>: Performs security monitoring and intrusion detection checks.<br/>"
        "• <b>BrakeController_Step (10ms Periodic)</b>: Closed-loop deceleration actuation with predictive braking inputs.",
        body_style
    ))
    
    doc.build(story)
    print(f"Generated sample HLD v3.0 at: {output_path}")


if __name__ == "__main__":
    v1_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v1.0.pdf")
    v2_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v2.0.pdf")
    v3_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v3.0.pdf")
    build_hld_v1(v1_path)
    build_hld_v2(v2_path)
    build_hld_v3(v3_path)
