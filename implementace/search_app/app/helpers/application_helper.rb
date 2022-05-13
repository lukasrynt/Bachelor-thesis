# frozen_string_literal: true

module ApplicationHelper
  include Pagy::Frontend

  def flash_class_for(type)
    case type
    when 'notice'
      'alert alert-info'
    when 'alert'
      'alert alert-danger'
    else
      "alert alert-#{type}"
    end
  end
end
