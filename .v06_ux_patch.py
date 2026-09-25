from pathlib import Path

root = Path('source')

def replace(path: str, old: str, new: str):
    p = root / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'Patch target not found: {path}: {old[:80]!r}')
    p.write_text(s.replace(old, new))

# Version bump
replace('app/build.gradle.kts', 'versionCode = 5', 'versionCode = 6')
replace('app/build.gradle.kts', 'versionName = "0.5.0"', 'versionName = "0.6.0"')

# Smooth page-to-page navigation.
p = root / 'app/src/main/java/com/jepongdevxyz/vidcrate/ui/DevxyzCrateApp.kt'
s = p.read_text()
s = s.replace(
    'import androidx.compose.runtime.*',
    'import androidx.compose.animation.AnimatedContent\nimport androidx.compose.animation.fadeIn\nimport androidx.compose.animation.fadeOut\nimport androidx.compose.animation.togetherWith\nimport androidx.compose.animation.core.tween\nimport androidx.compose.runtime.*',
)
old = '''        when (page) {
            AppPage.PROJECTS -> ProjectsScreen(
                project = state.project,
                onNewProject = { page = AppPage.NEW_PROJECT },
                onOpenProject = { page = AppPage.EDITOR },
                onNavigate = ::navigate,
            )
            AppPage.NEW_PROJECT -> NewProjectScreen(
                onBack = { page = AppPage.PROJECTS },
                onCreate = ::createAndOpen,
            )
            AppPage.EDITOR -> EditorScreen(viewModel, onBack = { page = AppPage.PROJECTS })
            AppPage.TEMPLATES -> TemplatesScreen(
                onBack = { page = AppPage.PROJECTS },
                onCreateTemplate = ::createAndOpen,
                onNavigate = ::navigate,
            )
            AppPage.LIBRARY -> LibraryScreen(
                project = state.project,
                onBack = { page = AppPage.PROJECTS },
                onOpenProject = { page = AppPage.EDITOR },
                onNavigate = ::navigate,
            )
            AppPage.SETTINGS -> SettingsScreen(
                onBack = { page = AppPage.PROJECTS },
                onNavigate = ::navigate,
            )
        }'''
new = '''        AnimatedContent(
            targetState = page,
            transitionSpec = { fadeIn(tween(180)) togetherWith fadeOut(tween(120)) },
            label = "page-transition",
        ) { target ->
            when (target) {
                AppPage.PROJECTS -> ProjectsScreen(
                    project = state.project,
                    onNewProject = { page = AppPage.NEW_PROJECT },
                    onOpenProject = { page = AppPage.EDITOR },
                    onNavigate = ::navigate,
                )
                AppPage.NEW_PROJECT -> NewProjectScreen(
                    onBack = { page = AppPage.PROJECTS },
                    onCreate = ::createAndOpen,
                )
                AppPage.EDITOR -> EditorScreen(viewModel, onBack = { page = AppPage.PROJECTS })
                AppPage.TEMPLATES -> TemplatesScreen(
                    onBack = { page = AppPage.PROJECTS },
                    onCreateTemplate = ::createAndOpen,
                    onNavigate = ::navigate,
                )
                AppPage.LIBRARY -> LibraryScreen(
                    project = state.project,
                    onBack = { page = AppPage.PROJECTS },
                    onOpenProject = { page = AppPage.EDITOR },
                    onNavigate = ::navigate,
                )
                AppPage.SETTINGS -> SettingsScreen(
                    onBack = { page = AppPage.PROJECTS },
                    onNavigate = ::navigate,
                )
            }
        }'''
if old not in s:
    raise SystemExit('DevxyzCrateApp page block not found')
p.write_text(s.replace(old, new))

# Smooth editor interactions: back prioritizes closing the active layer, animated contextual tools,
# haptic tool selection, continuous scrubbing, pinch-to-zoom and playhead-following timeline.
p = root / 'app/src/main/java/com/jepongdevxyz/vidcrate/ui/EditorScreen.kt'
s = p.read_text()
s = s.replace('import androidx.activity.compose.rememberLauncherForActivityResult', 'import androidx.activity.compose.BackHandler\nimport androidx.activity.compose.rememberLauncherForActivityResult')
s = s.replace('import androidx.compose.foundation.BorderStroke', 'import androidx.compose.animation.AnimatedVisibility\nimport androidx.compose.animation.fadeIn\nimport androidx.compose.animation.fadeOut\nimport androidx.compose.animation.slideInVertically\nimport androidx.compose.animation.slideOutVertically\nimport androidx.compose.animation.core.tween\nimport androidx.compose.foundation.BorderStroke')
s = s.replace('import androidx.compose.foundation.gestures.detectTapGestures', 'import androidx.compose.foundation.gestures.detectDragGestures\nimport androidx.compose.foundation.gestures.detectTapGestures\nimport androidx.compose.foundation.gestures.detectTransformGestures')
s = s.replace('import androidx.compose.ui.platform.LocalDensity', 'import androidx.compose.ui.platform.LocalDensity\nimport androidx.compose.ui.platform.LocalHapticFeedback')
s = s.replace('import androidx.compose.ui.text.font.FontStyle', 'import androidx.compose.ui.hapticfeedback.HapticFeedbackType\nimport androidx.compose.ui.text.font.FontStyle')
s = s.replace(
'''    var exportOpen by remember { mutableStateOf(false) }
    var isPlaying by remember { mutableStateOf(false) }
    val snackbar = remember { SnackbarHostState() }''',
'''    var exportOpen by remember { mutableStateOf(false) }
    var isPlaying by remember { mutableStateOf(false) }
    val snackbar = remember { SnackbarHostState() }
    val haptics = LocalHapticFeedback.current

    BackHandler(enabled = tool != null || exportOpen || state.selectedClipId != null) {
        when {
            tool != null -> tool = null
            exportOpen -> exportOpen = false
            state.selectedClipId != null -> viewModel.selectClip(null)
        }
    }''')
s = s.replace(
'''                PreviewStage(state, viewModel, isPlaying) { isPlaying = it }
                TransportRow(state, viewModel, isPlaying) { isPlaying = !isPlaying }
                if (state.selectedClipId != null) SelectedClipBar(viewModel)
                TimelineArea(state, viewModel, Modifier.weight(1f))
                EditorAssetBar(selected = tool, onTool = { tool = if (tool == it) null else it })''',
'''                PreviewStage(state, viewModel, isPlaying) { isPlaying = it }
                TransportRow(state, viewModel, isPlaying) { isPlaying = !isPlaying }
                AnimatedVisibility(
                    visible = state.selectedClipId != null,
                    enter = slideInVertically(tween(160)) { -it / 2 } + fadeIn(tween(140)),
                    exit = slideOutVertically(tween(120)) { -it / 2 } + fadeOut(tween(100)),
                ) { SelectedClipBar(viewModel) }
                TimelineArea(state, viewModel, isPlaying, Modifier.weight(1f))
                EditorAssetBar(selected = tool, onTool = {
                    haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                    tool = if (tool == it) null else it
                })''')
s = s.replace(
'''            if (tool != null) {
                ToolPanel(
                    modifier = Modifier.fillMaxSize(),
                    tool = tool!!,
                    state = state,
                    viewModel = viewModel,
                    onClose = { tool = null },
                    onImportVideo = { videoPicker.launch(arrayOf("video/*")) },
                    onImportPhoto = { photoPicker.launch(arrayOf("image/*")) },
                    onImportOverlay = { overlayPicker.launch(arrayOf("image/*", "video/*")) },
                    onImportAudio = { audioPicker.launch(arrayOf("audio/*")) },
                )
            }''',
'''            AnimatedVisibility(
                visible = tool != null,
                enter = slideInVertically(tween(220)) { it } + fadeIn(tween(160)),
                exit = slideOutVertically(tween(180)) { it } + fadeOut(tween(120)),
            ) {
                tool?.let { activeTool ->
                    ToolPanel(
                        modifier = Modifier.fillMaxSize(),
                        tool = activeTool,
                        state = state,
                        viewModel = viewModel,
                        onClose = { tool = null },
                        onImportVideo = { videoPicker.launch(arrayOf("video/*")) },
                        onImportPhoto = { photoPicker.launch(arrayOf("image/*")) },
                        onImportOverlay = { overlayPicker.launch(arrayOf("image/*", "video/*")) },
                        onImportAudio = { audioPicker.launch(arrayOf("audio/*")) },
                    )
                }
            }''')
s = s.replace(
'''        Row(Modifier.fillMaxWidth().height(38.dp).horizontalScroll(rememberScrollState()).padding(horizontal = 5.dp), verticalAlignment = Alignment.CenterVertically) {
            MiniAction(Icons.Rounded.ContentCut, "Split", viewModel::splitSelected)''',
'''        Row(Modifier.fillMaxWidth().height(40.dp).horizontalScroll(rememberScrollState()).padding(horizontal = 5.dp), verticalAlignment = Alignment.CenterVertically) {
            MiniAction(Icons.Rounded.Close, "Done", onClick = { viewModel.selectClip(null) })
            MiniAction(Icons.Rounded.ContentCut, "Split", viewModel::splitSelected)''')
s = s.replace('private fun TimelineArea(state: EditorUiState, viewModel: EditorViewModel, modifier: Modifier = Modifier) {', 'private fun TimelineArea(state: EditorUiState, viewModel: EditorViewModel, isPlaying: Boolean, modifier: Modifier = Modifier) {')
s = s.replace(
'''    val contentWidth = (minDuration / 1000f * zoom + 120f).dp

    Surface(modifier.fillMaxWidth(), color = Color(0xFF071016), border = BorderStroke(1.dp, DxStrokeSoft)) {''',
'''    val contentWidth = (minDuration / 1000f * zoom + 120f).dp

    LaunchedEffect(isPlaying, state.playheadMs, zoom, scroll.maxValue) {
        if (isPlaying && scroll.maxValue > 0) {
            val playheadPx = with(density) { (state.playheadMs / 1000f * zoom).dp.toPx() }
            val target = (playheadPx - 220f).toInt().coerceIn(0, scroll.maxValue)
            if (kotlin.math.abs(scroll.value - target) > 90) scroll.animateScrollTo(target)
        }
    }

    Surface(modifier.fillMaxWidth(), color = Color(0xFF071016), border = BorderStroke(1.dp, DxStrokeSoft)) {''')
s = s.replace(
'''                Column(
                    Modifier.width(contentWidth).fillMaxHeight().pointerInput(zoom, state.project.durationMs) {
                        detectTapGestures { offset ->
                            val secondPx = with(density) { zoom.dp.toPx() }
                            val ms = ((offset.x / secondPx) * 1000f).toLong()
                            viewModel.setPlayhead(ms)
                        }
                    }
                ) {''',
'''                Column(
                    Modifier.width(contentWidth).fillMaxHeight()
                        .pointerInput(zoom, state.project.durationMs) {
                            detectTapGestures { offset ->
                                val secondPx = with(density) { zoom.dp.toPx() }
                                viewModel.setPlayhead(((offset.x / secondPx) * 1000f).toLong())
                            }
                        }
                        .pointerInput(zoom, state.project.durationMs) {
                            detectDragGestures { change, _ ->
                                change.consume()
                                val secondPx = with(density) { zoom.dp.toPx() }
                                viewModel.setPlayhead(((change.position.x / secondPx) * 1000f).toLong())
                            }
                        }
                        .pointerInput(zoom) {
                            detectTransformGestures { _, _, zoomChange, _ ->
                                if (kotlin.math.abs(zoomChange - 1f) > 0.01f) viewModel.setZoom(zoom * zoomChange)
                            }
                        }
                ) {''')
p.write_text(s)

# Animate panel content changes and make import actions self-explanatory.
p = root / 'app/src/main/java/com/jepongdevxyz/vidcrate/ui/EditorPanels.kt'
s = p.read_text()
s = s.replace('import androidx.compose.foundation.BorderStroke', 'import androidx.compose.animation.AnimatedContent\nimport androidx.compose.animation.fadeIn\nimport androidx.compose.animation.fadeOut\nimport androidx.compose.animation.togetherWith\nimport androidx.compose.animation.core.tween\nimport androidx.compose.foundation.BorderStroke')
s = s.replace(
'''            PanelHeader(panelTitle(tool), onClose)
            when (tool) {
                EditorTool.MEDIA -> MediaPanel(state, viewModel, onImportVideo, onImportPhoto, onImportOverlay, onImportAudio)
                EditorTool.SOUNDS -> SoundsPanel(state, viewModel, onImportAudio)
                EditorTool.TEXT -> TextPanel(state, viewModel)
                EditorTool.STICKERS -> StickersPanel(state, viewModel, onImportOverlay)
                EditorTool.EFFECTS -> EffectsPanel(state, viewModel)
                EditorTool.CAPTIONS -> CaptionsPanel(state, viewModel)
                EditorTool.ADJUST -> VideoPropertiesPanel(state, viewModel)
                EditorTool.SETTINGS -> EditorSettingsPanel(state, viewModel)
            }''',
'''            PanelHeader(panelTitle(tool), onClose)
            AnimatedContent(
                targetState = tool,
                transitionSpec = { fadeIn(tween(150)) togetherWith fadeOut(tween(100)) },
                label = "tool-panel-content",
            ) { activeTool ->
                when (activeTool) {
                    EditorTool.MEDIA -> MediaPanel(state, viewModel, onImportVideo, onImportPhoto, onImportOverlay, onImportAudio)
                    EditorTool.SOUNDS -> SoundsPanel(state, viewModel, onImportAudio)
                    EditorTool.TEXT -> TextPanel(state, viewModel)
                    EditorTool.STICKERS -> StickersPanel(state, viewModel, onImportOverlay)
                    EditorTool.EFFECTS -> EffectsPanel(state, viewModel)
                    EditorTool.CAPTIONS -> CaptionsPanel(state, viewModel)
                    EditorTool.ADJUST -> VideoPropertiesPanel(state, viewModel)
                    EditorTool.SETTINGS -> EditorSettingsPanel(state, viewModel)
                }
            }''')
s = s.replace('ImportWide(Icons.Rounded.Upload, "Import", onImportVideo)', 'ImportWide(Icons.Rounded.Upload, "Import media", onImportVideo)')
p.write_text(s)

print('Applied DevxyzCrate v0.6 smooth UX patch')
