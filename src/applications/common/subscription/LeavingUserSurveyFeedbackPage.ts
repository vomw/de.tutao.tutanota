import { emitWizardEvent, WizardEventType, WizardPageAttrs, WizardPageN } from "../../../ui/base/WizardDialog.js"
import { LeavingUserSurveyData } from "./LeavingUserSurveyWizard.js"
import m, { Vnode, VnodeDOM } from "mithril"
import { HtmlEditor, HtmlEditorMode } from "../../../ui/editor/HtmlEditor.js"
import { CATEGORY_TO_IMAGE, getCategoryType } from "./LeavingUserSurveyConstants.js"
import { Styles } from "../../../ui/styles.js"
import { SetupLeavingUserSurveyPage } from "./SetupLeavingUserSurveyPage.js"
import { getHtmlSanitizer } from "../misc/HtmlSanitizer"

export class LeavingUserSurveyFeedbackPage implements WizardPageN<LeavingUserSurveyData> {
	private _dom: HTMLElement | null = null
	private readonly customReasonEditor: HtmlEditor

	constructor() {
		let NUMBER_OF_EDITOR_LINES = Styles.get().isDesktopLayout() ? 5 : 1
		this.customReasonEditor = new HtmlEditor(getHtmlSanitizer())
			.setStaticNumberOfLines(NUMBER_OF_EDITOR_LINES)
			.showBorders()
			.setPlaceholderId("enterDetails_msg")
			.setMode(HtmlEditorMode.HTML)
			.setHtmlMonospace(false)
			.setValue("")
	}

	oncreate(vnode: VnodeDOM<WizardPageAttrs<LeavingUserSurveyData>>) {
		this._dom = vnode.dom as HTMLElement
	}

	oninit(vnode: Vnode<WizardPageAttrs<LeavingUserSurveyData>>) {
		//Other reason, only set to avoid error thrown
		vnode.attrs.data.reason = "33"
	}

	view(vnode: Vnode<WizardPageAttrs<LeavingUserSurveyData>>) {
		return m(
			SetupLeavingUserSurveyPage,
			{
				closeAction: () => {
					vnode.attrs.data.details = this.customReasonEditor.getValue()
					vnode.attrs.data.submitted = true
					this.closeDialog()
				},
				skipAction: () => this.closeDialog(),
				nextButtonLabel: "submit_action",
				nextButtonEnabled: true,
				image: CATEGORY_TO_IMAGE.get(getCategoryType(vnode.attrs.data.category!))?.image!,
				imageStyle: {
					paddingBottom: "60px",
				},
				mainMessage: CATEGORY_TO_IMAGE.get(getCategoryType(vnode.attrs.data.category!))?.translationKey!,
				secondaryMessage: "surveyReasonSecondaryMessage_label",
			},
			m(".pt-16", m(this.customReasonEditor)),
		)
	}

	closeDialog(): void {
		if (this._dom) {
			emitWizardEvent(this._dom, WizardEventType.CLOSE_DIALOG)
		}
	}
}
