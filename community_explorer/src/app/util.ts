/*
 *
 * utils.ts
 *
 * Utility functions
 *
 */

export const addReactSelectKeys = (
  option: {} | {}[] = {},
  keyMapping: Record<'label' | 'value', string> = {
    label: 'name',
    value: 'slug',
  },
) => {
  const options = Array.isArray(option) ? option : [option];
  return options.map(opt =>
    Object.assign(
      {
        label: keyMapping.label ? option[keyMapping.label] : undefined,
        value: keyMapping.value ? option[keyMapping.value] : undefined,
      },
      opt,
    ),
  );
};
