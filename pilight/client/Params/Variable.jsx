import PropTypes from 'prop-types';
import React from 'react';
import {FormControl} from 'react-bootstrap';

import {Float} from './Float';

import css from './common.scss';


export class Variable extends React.Component {
    static propTypes = {
        onChange: PropTypes.func.isRequired,
        variable: PropTypes.shape({
            variableId: PropTypes.number,
            multiply: PropTypes.any,
            add: PropTypes.any,
        }).isRequired,
        variables: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }),
        ),
    };

    onVariableChange = (event) => {
        this.props.onChange({
            ...this.props.variable,
            variableId: parseInt(event.target.value, 10),
        });
    };

    onMultiplyChange = (value) => {
        this.props.onChange({
            ...this.props.variable,
            multiply: value,
        });
    };

    onAddChange = (value) => {
        this.props.onChange({
            ...this.props.variable,
            add: value,
        });
    };

    render() {
        const variableOptions = this.props.variables ? this.props.variables.map((variable) => {
            return (
                <option key={variable.id} value={variable.id.toString()}>
                    {variable.name}
                </option>
            );
        }) : [];
        return (
            <div>
                <FormControl
                    bsSize="small"
                    className={css.controlWidth}
                    componentClass="select"
                    onChange={this.onVariableChange}
                    value={this.props.variable.variableId ? this.props.variable.variableId.toString() : ''}
                >
                    <option value="">None</option>
                    {variableOptions}
                </FormControl>
                <Float
                    onChange={this.onMultiplyChange}
                    origValue={1}
                    value={this.props.variable.multiply}
                />
                <Float
                    onChange={this.onAddChange}
                    origValue={0}
                    value={this.props.variable.add}
                />
            </div>
        );
    }
}
