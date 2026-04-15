from .processor import process_field_driven_sample_plan

DISPATCHER = {
    "field_driven_sample_plan": process_field_driven_sample_plan,
    # 未来可以添加其他类型的模板处理器
}