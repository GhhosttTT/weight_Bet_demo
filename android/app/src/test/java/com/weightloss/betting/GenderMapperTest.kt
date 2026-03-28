package com.weightloss.betting

import com.weightloss.betting.util.GenderMapper
import org.junit.Test
import org.junit.Assert.*

/**
 * GenderMapper 单元测试
 * 测试性别显示和后端值的映射功能
 */
class GenderMapperTest {

    // ==================== 显示值转后端值测试 ====================

    @Test
    fun `test_male_display_to_value`() {
        val result = GenderMapper.toValue("男")
        assertEquals("male", result)
    }

    @Test
    fun `test_female_display_to_value`() {
        val result = GenderMapper.toValue("女")
        assertEquals("female", result)
    }

    @Test
    fun `test_unknown_display_to_value_returns_default`() {
        val result = GenderMapper.toValue("其他")
        assertEquals("male", result)
    }

    @Test
    fun `test_empty_display_to_value_returns_default`() {
        val result = GenderMapper.toValue("")
        assertEquals("male", result)
    }

    @Test
    fun `test_null_display_to_value_returns_default`() {
        val result = GenderMapper.toValue(null)
        assertEquals("male", result)
    }

    // ==================== 后端值转显示值测试 ====================

    @Test
    fun `test_male_value_to_display`() {
        val result = GenderMapper.toDisplay("male")
        assertEquals("男", result)
    }

    @Test
    fun `test_female_value_to_display`() {
        val result = GenderMapper.toDisplay("female")
        assertEquals("女", result)
    }

    @Test
    fun `test_unknown_value_to_display_returns_default`() {
        val result = GenderMapper.toDisplay("other")
        assertEquals("未设置", result)
    }

    @Test
    fun `test_empty_value_to_display_returns_default`() {
        val result = GenderMapper.toDisplay("")
        assertEquals("未设置", result)
    }

    @Test
    fun `test_null_value_to_display_returns_default`() {
        val result = GenderMapper.toDisplay(null)
        assertEquals("未设置", result)
    }

    // ==================== 位置测试 ====================

    @Test
    fun `test_get_position_male`() {
        val position = GenderMapper.getPosition("male")
        assertEquals(0, position)
    }

    @Test
    fun `test_get_position_female`() {
        val position = GenderMapper.getPosition("female")
        assertEquals(1, position)
    }

    @Test
    fun `test_get_position_unknown_returns_0`() {
        val position = GenderMapper.getPosition("other")
        assertEquals(0, position)
    }

    @Test
    fun `test_get_position_null_returns_0`() {
        val position = GenderMapper.getPosition(null)
        assertEquals(0, position)
    }

    // ==================== 显示选项测试 ====================

    @Test
    fun `test_display_options_count`() {
        assertEquals(2, GenderMapper.displayOptions.size)
    }

    @Test
    fun `test_display_options_contains_male`() {
        assertTrue(GenderMapper.displayOptions.contains("男"))
    }

    @Test
    fun `test_display_options_contains_female`() {
        assertTrue(GenderMapper.displayOptions.contains("女"))
    }

    @Test
    fun `test_display_options_does_not_contain_other`() {
        assertFalse(GenderMapper.displayOptions.contains("其他"))
    }

    // ==================== 完整流程测试 ====================

    @Test
    fun `test_complete_round_trip_male`() {
        val display = "男"
        val value = GenderMapper.toValue(display)
        val resultDisplay = GenderMapper.toDisplay(value)
        assertEquals(display, resultDisplay)
    }

    @Test
    fun `test_complete_round_trip_female`() {
        val display = "女"
        val value = GenderMapper.toValue(display)
        val resultDisplay = GenderMapper.toDisplay(value)
        assertEquals(display, resultDisplay)
    }
}
