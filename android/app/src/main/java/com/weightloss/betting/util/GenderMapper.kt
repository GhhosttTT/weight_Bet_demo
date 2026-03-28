package com.weightloss.betting.util

object GenderMapper {
    
    private val displayToValueMap = mapOf(
        "男" to "male",
        "女" to "female"
    )
    
    private val valueToDisplayMap = mapOf(
        "male" to "男",
        "female" to "女"
    )
    
    val displayOptions = listOf("男", "女")
    
    fun toValue(display: String?): String {
        if (display == null) return "male"
        return displayToValueMap[display] ?: "male"
    }
    
    fun toDisplay(value: String?): String {
        if (value == null) return "未设置"
        return valueToDisplayMap[value] ?: "未设置"
    }
    
    fun getPosition(value: String?): Int {
        val display = toDisplay(value)
        val position = displayOptions.indexOf(display)
        return if (position >= 0) position else 0
    }
}
