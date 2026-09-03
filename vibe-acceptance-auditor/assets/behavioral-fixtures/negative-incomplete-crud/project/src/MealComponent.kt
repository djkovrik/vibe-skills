interface MealComponent {
    fun createPreset(name: String)
    fun loadPresets(): List<String>
    fun deletePreset(name: String)
    fun createDraft()
    fun loadDraft(): String?
}
