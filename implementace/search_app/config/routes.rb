# frozen_string_literal: true

Rails.application.routes.draw do
  resources :documents, only: %i[index show] do
    collection do
      get :search
    end
  end
  resources :collections, only: %i[index show] do
    member do
      get :generate_index
      get :show_index
    end
  end

  root 'collections#index'
end
