import React from 'react';

const ModelSelector = ({ models, selectedModel, onModelChange }) => {
  // Group models by provider
  const groupedModels = models.reduce((acc, model) => {
    if (!acc[model.provider]) {
      acc[model.provider] = [];
    }
    acc[model.provider].push(model);
    return acc;
  }, {});

  const handleModelChange = (e) => {
    const [modelId, provider] = e.target.value.split('|');
    onModelChange(modelId, provider);
  };

  return (
    <div className="flex items-center space-x-3">
      <label htmlFor="model-selector" className="font-medium text-gray-700">
        Model:
      </label>
      <select
        id="model-selector"
        className="border border-gray-300 rounded-md px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={`${selectedModel}|${models.find(m => m.id === selectedModel)?.provider || ''}`}
        onChange={handleModelChange}
      >
        {Object.keys(groupedModels).map((provider) => (
          <optgroup key={provider} label={provider.charAt(0).toUpperCase() + provider.slice(1)}>
            {groupedModels[provider].map((model) => (
              <option key={model.id} value={`${model.id}|${model.provider}`}>
                {model.name}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;